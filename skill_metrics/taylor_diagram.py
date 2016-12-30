import numpy as np
from skill_metrics import check_taylor_stats
from skill_metrics import get_taylor_diagram_axes
from skill_metrics import get_taylor_diagram_options
from skill_metrics import overlay_taylor_diagram_circles
from skill_metrics import overlay_taylor_diagram_lines
from skill_metrics import plot_pattern_diagram_colorbar
from skill_metrics import plot_pattern_diagram_markers
from skill_metrics import plot_taylor_axes

def taylor_diagram(*args, **kwargs):
    '''
    Plot a Taylor diagram from statistics of different series.
    
    taylor_diagram(STDs,RMSs,CORs,keyword=value)
    
    The first 3 arguments must be the inputs as described below followed by
    keywords in the format OPTION = value. An example call to the function 
    would be:
    
    taylor_diagram(STDs,RMSs,CORs,markerdisplayed='marker')
    
    INPUTS:
    STDs: Standard deviations
    RMSs: Centered Root Mean Square Difference 
    CORs: Correlation
    
    Each of these inputs are one-dimensional with the same length. First
    index corresponds to the reference series for the diagram. For 
    example STDs[1] is the standard deviation of the reference series 
    and STDs[2:N] are the standard deviations of the other series. Note 
    that only the latter are plotted.
 
    Note that by definition the following relation must be true for all 
    series i:

     RMSs(i) = sqrt(STDs(i).^2 + STDs(1)^2 - 2*STDs(i)*STDs(1).*CORs(i))

    This relation is checked if the checkStats option is used, and if not 
    verified an error message is sent. This relation is not checked by
    default. Please see Taylor's JGR article for more informations about 
    this relation.
    
    OUTPUTS:
    None.
    
    LIST OF OPTIONS:
    For an exhaustive list of options to customize your diagram, call the 
    function without arguments at a Python command line:
    >> target_diagram
    
    Reference:
 
    Taylor, K. E. (2001), Summarizing multiple aspects of model 
      performance in a single diagram, J. Geophys. Res., 106(D7),
      7183-7192, doi:10.1029/2000JD900719.

    ToDo: Investigate adding ALLSTATS function that is available from 
          http://codes.guillaumemaze.org/matlab
    
    Author: Peter A. Rochford
        Symplectic, LLC
        www.thesymplectic.com
        prochford@thesymplectic.com

    Created on Dec 3, 2016
    '''

    # Check for number of arguments
    nargin = len(args)
    STDs, RMSs, CORs = _get_taylor_diagram_arguments(*args,**kwargs)
    if nargin == 0: return

    # Get options
    option = get_taylor_diagram_options(CORs,**kwargs)
#    print option # debug
# 
    # Check the input statistics if requested.
    if option['checkstats'] == 'on':
        check_taylor_stats(STDs[1:], RMSs[1:], CORs[1:], 0.01)

    # Express statistics in polar coordinates.
    rho   = STDs
    theta = np.arccos(CORs)

    #  Get axis values for plot
    axes, cax = get_taylor_diagram_axes(rho,option)
     
    # Plot axes for target diagram
    if option['overlay'] == 'off':
        # Draw circles about origin
        overlay_taylor_diagram_circles(axes,cax,option)
     
        # Draw lines emanating from origin
        overlay_taylor_diagram_lines(axes,cax,option);
     
        # Plot axes for Taylor diagram
        plot_taylor_axes(axes,cax,option)

    # Plot data points. Note that only rho[1:N] and theta[1:N] are plotted.
    X = np.multiply(rho[1:],np.cos(theta[1:]))
    Y = np.multiply(rho[1:],np.sin(theta[1:]))

    lowcase = option['markerdisplayed'].lower()
    if lowcase == 'marker':
        plot_pattern_diagram_markers(X,Y,option)
    elif lowcase == 'colorbar':
        plot_pattern_diagram_colorbar(X,Y,RMSs[1:],option)
    else:
        raise ValueError('Unrecognized option: ' + 
                         option['markerdisplayed'])

def _get_taylor_diagram_arguments(*args,**kwargs):
    '''
    Get arguments for taylor_diagram function.
    
    Retrieves the arguments supplied to the TAYLOR_DIAGRAM function as
    arguments and displays the optional arguments if none are supplied.
    Otherwise, tests the first 3 arguments are numeric quantities and 
    returns their values.
    
    INPUTS:
    args : variable-length input argument list
    
    OUTPUTS:
    STDs: Standard deviations
    RMSs: Centered Root Mean Square Difference 
    CORs: Correlation
    '''
    
    import numbers
    
    STDs=[]; RMSs=[]; CORs=[];
    nargin = len(args)
    if nargin == 0:
        # Display options list
        _display_taylor_diagram_options()
        return STDs, RMSs, CORs
    elif nargin != 3:
        raise ValueError('Must supply 3 arguments.')

    STDs = args[0]
    RMSs = args[1]
    CORs = args[2]

    # Test the above are numeric quantities
    if isinstance(STDs, numbers.Number):
        STDs = np.array(STDs,ndmin=1)
    if not isinstance(STDs, np.ndarray):
        raise ValueError('Argument STDs is not a numeric array')

    if isinstance(RMSs, numbers.Number):
        RMSs = np.array(RMSs,ndmin=1)
    if not isinstance(RMSs, np.ndarray):
        raise ValueError('Argument RMSs is not a numeric array')
 
    if isinstance(CORs, numbers.Number):
        CORs = np.array(CORs,ndmin=1)
    if not isinstance(CORs, np.ndarray):
        raise ValueError('Argument CORs is not a numeric array')

    return STDs, RMSs, CORs

def _display_taylor_diagram_options():
    '''
    Displays available options for TAYLOR_DIAGRAM function.
    '''
    
    _disp('General options:')
    _dispopt("'numberPanels'",'1 or 2: Panels to display (1 for ' +
             'positive correlations, 2 for positive and negative' +
             ' correlations). \n\t\tDefault value depends on ' +
             'correlations (CORs)')
    _dispopt("'overlay'","'on' / 'off' (default): " +
        'Switch to overlay current statistics on Taylor diagram. ' +
        '\n\t\tOnly markers will be displayed.')
    
    _disp('Marker options:')
    _dispopt("'MarkerDisplayed'",
        "'marker' (default): Experiments are represented by individual " + 
        "symbols\n\t\t"  + 
        "'colorBar': Experiments are represented by a color described " + \
        "in a colorbar")
    _disp("OPTIONS when 'MarkerDisplayed' == 'marker'")
    _dispopt("'markerLabel'",'Labels for markers')
    _dispopt("'markerLabelColor'",'Marker label color (Default: black)')
    _dispopt("'markerColor'",'Single color to use for all markers'  +
        ' (Default: red)')
    _dispopt("'markerLegend'","'on' / 'off' (default): "  +
        'Use legend for markers')
    _disp("OPTIONS when MarkerDisplayed' == 'colorbar'")
    _dispopt("'nonRMSDz'","'on'/ 'off' (default): "  + 
        'Values in RMSDz do not correspond to total RMS Differences.\n\t\t'  +
        '(Used to make range of RMSDz values appear above color bar.)')
    _dispopt("'titleColorBar'",'Title of the colorbar.')
     
    _disp('RMS axis options:')
    _dispopt("'tickRMS'",'RMS values to plot gridding circles from ' +
             'observation point')
    _dispopt("'colRMS'",'RMS grid and tick labels color. (Default: green)')
    _dispopt("'showlabelsRMS'","'on' (default) / 'off': "  +
        'Show the RMS tick labels')
    _dispopt("'tickRMSangle'",'Angle for RMS tick labels with the ' +
             'observation point. Default: 135 deg.')
    _dispopt("'styleRMS'",'Linestyle of the RMS grid')
    _dispopt("'widthRMS'",'Line width of the RMS grid')
    _dispopt("'titleRMS'","'on' (default) / 'off': "  +
        'Show RMSD axis title')
     
    _disp('STD axis options:')
    _dispopt("'tickSTD'",'STD values to plot gridding circles from ' + 
             'origin')
    _dispopt("'colSTD'",'STD grid and tick labels color. (Default: black)')
    _dispopt("'showlabelsSTD'","'on' (default) / 'off': "  +
        'Show the STD tick labels')
    _dispopt("'styleSTD'",'Linestyle of the STD grid')
    _dispopt("'widthSTD'",'Line width of the STD grid')
    _dispopt("'titleSTD'","'on' (default) / 'off': "  +
        'Show STD axis title')
    _dispopt("'limSTD'",'Max of the STD axis (radius of the largest ' +
             'circle)')
     
    _disp('CORRELATION axis options:')
    _dispopt("'tickCOR'",'CORRELATON grid values')
    _dispopt("'colCOR'",'CORRELATION grid color. Default: blue')
    _dispopt("'showlabelsCOR'","'on' (default) / 'off': "  +
        'Show the CORRELATION tick labels')
    _dispopt("'styleCOR'",'Linestyle of the COR grid')
    _dispopt("'widthCOR'",'Line width of the COR grid')
    _dispopt("'titleCOR'","'on' (default) / 'off': "  +
        'Show CORRELATION axis title')
     
    _disp('CONTROL options:')
    _dispopt("'checkStats'","'on' / 'off' (default): "  +
        'Check input statistics satisfy Taylor relationship')

def _disp(text):
    print text

def _dispopt(optname,optval):
    '''
    Displays option name and values

    This is a support function for the DISPLAY_TARGET_DIAGRAM_OPTIONS function.
    It displays the option name OPTNAME on a line by itself followed by its 
    value OPTVAL on the following line.
    '''

    _disp('\t%s' % optname)
    _disp('\t\t%s' % optval)
