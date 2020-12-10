#! /usr/bin/env python3

import numpy as np

import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.transforms import Bbox, BboxTransformFrom, blended_transform_factory

driver_names = ['Mvk_Sky', 'Lanx12fps', 'T2The', 'mcswim7', 'Wingn', 'j_fern', 'IP_3010',
                'CaliRob187', 'ConwayTwitty', 'tdarsin', '007Mech', 'tinydarthspike', 'Xotic', 'justjose_x', 'RR_Silent']

RRP_PLAYERS = {
    (0, 9, 73): 'Teek9296',
    (0, 9, 38): 'Teek9296',
    (0, 14, 13): "xarescka",
    (1, 22, 1): "Mvk_Sky",
    (1, 88, 10): "The_ConwayTwitty",
    (2, 70, 1): "mcswim7",
    (2, 14, 1): "RR_Silent",
    (3, 9, 2): "tdarsin",
    (3, 14, 1): "CaliRob187",
    (4, 36, 1): "T2The",
    (4, 88, 16): "007Mech",
    (5, 22, 1): "tinydarthspike",
    (5, 95, 29): "xKachow95",
    (5, 21, 1): "capitahood",
    (6, 19, 1): "XoticFlame2919",
    (6, 69, 14): "justjose_x",
    (6, 95, 29): "xKachow95",
    (9, 95, 29): "xKachow95",
    (7, 21, 1): "j_fern",
    (7, 13, 1): "wingnnn7",
    (8, 30, 1): "IP_3010",
    (8, 21, 28): "Powaup",
    (9, 2, 1): "Lanx12fps",
    (9, 22, 11): "sharikiki20",
}

Colours = {
    0 : (0,210,190), # 'Mercedes',
    1 : (192,0,0), # 'Ferrari',
    2 : (6,0,239), # 'Red Bull Racing',
    3 : (0,130,250), # 'Williams',
    4 : (245,150,200), # 'Racing Point',
    5 : (255,245,0), # 'Renault',
    6 : (200,200,200), # 'Toro Rosso',
    7 : (120,120,120), # 'Haas',
    8 : (255,135,0), # 'McLaren',
    9 : (150,0,0), # 'Alfa Romeo',
    255 : (0, 255, 0)
}
for key, rgb in Colours.items():
    Colours[key] = tuple(c/255 for c in rgb)

class PicaAxes(object):
    """
    Add text to axes using a pica/point based coordinate system.
    """
        
    _anchor_funcs = {
        'bl' : lambda f,a: (f-a[0]),
        'tl' : lambda f,a: (f-a.diagonal()),
        'tr' : lambda f,a: (f-a[1]),
        'br' : lambda f,a: (f-a.flatten()[[2,1]]),
    }
    
    def __init__(self, spacing=12, size=10, ax=None):
        """docstring"""
        
        if ax == None:
            self.ax = plt.gca()
        else:
            self.ax = ax

        self.fig = ax.figure
        self.spacing = spacing
        self.size = size
        self._dpi = self.fig._dpi
        
        self.fpos = None
        self.apos = None
        self.get_positions()
        
        self.anchor = {}
        self.get_anchors()
    
    def get_positions(self):
        """docstring"""

        self.fpos = self.fig.bbox._points
        axis_position = self.ax.get_position()
        self.apos = self.fig.transFigure.transform(axis_position)
        
    def get_anchors(self):
        """docstring"""
        
        for key in self._anchor_funcs.keys():
            self.anchor[key] = self._anchor_funcs[key](self.fpos, self.apos)
            
    def trans(self, anchor='bl'):
        """docstring"""
        
        scale = self._dpi / (72/self.spacing)
        points = self.anchor[anchor] / scale
        bbox = Bbox(points)
        return BboxTransformFrom(bbox) + self.fig.transFigure      
    
    def text(self, *args, anchor='bl', **kwargs):
        """docstring"""
        
        return self.ax.text(*args, **kwargs, transform=self.trans(anchor))
    
    def textHorz(self, *args, anchor='bl', **kwargs):
        """docstring"""

        composite_trans = blended_transform_factory(self.trans(anchor), self.ax.transData)
        return self.ax.text(*args, **kwargs, transform=composite_trans)
        
    def textVert(self, *args, anchor='bl', **kwargs):
        """docstring"""

        composite_trans = blended_transform_factory(self.ax.transData, self.trans(anchor))
        return self.ax.text(*args, **kwargs, transform=composite_trans)
    
    # def plot(self, *args, anchor='bl', **kwargs):
    #     """docstring"""
        
    #     return self.ax.text(*args, **kwargs, transform=self.trans(anchor))
    
    # def plotHorz(self, *args, anchor='bl', **kwargs):
    #     """docstring"""

    #     composite_trans = blended_transform_factory(self.trans(anchor), self.ax.transData)
    #     return self.ax.text(*args, **kwargs, transform=composite_trans)
        
    # def plotVert(self, *args, anchor='bl', **kwargs):
    #     """docstring"""

    #     composite_trans = blended_transform_factory(self.ax.transData, self.trans(anchor))
    #     return self.ax.text(*args, **kwargs, transform=composite_trans)
    
#######################################################
def add_paxes(margins=[3, 3, 3, 3], fig=None):
    
    if fig == None:
        plt.gcf()

    x0,y0,x1,y1 = margins

    w,h = fig.get_size_inches()
    wu = (w*6)
    hu = (h*6)

    pos = [x0/wu, y0/hu, 1-((x0+x1)/wu), 1-((y0+y1)/hu)]
    return fig.add_axes(pos)

def plot_position_change(data=None, session=None, xtickpos=[], xticklabel=[]):

    xPen = np.array([1.02, 1.04]) * data["totalDistance"].max()
    
    x = []; y = []; c = []; labels = []; style = []
    for veh,grp in data.groupby('vehicleID'):
        if grp.empty:
            continue
        
        X = grp['totalDistance'].values
        Y = grp['carPosition'].values
        
        x.append((X[:-1], xPen))
        y.append((Y[:-1], Y[-2:]))
        c.append(veh.colour)
        style.append(veh.style)
        labels.append(veh.name)

    position = {
        1: '#D6AF36',
        2: '#A7A7AD',
        3: '#A77044',
        10: (1,1,1)
    }
    
    # rcParams["font.sans-serif"] = 'Helvetica Neue'
    rcParams["font.sans-serif"] = 'Avenir Next'
    plt.style.use("./f1.mplstyle")

    fig = plt.figure(figsize=(8,4))
    ax = add_paxes(fig=fig, margins=(3,3,10,4))
    pax = PicaAxes(ax=ax)

    lines = []
    names = []
    for i in range(len(x)):
        line1 = ax.plot(x[i][0], y[i][0], c=c[i], linestyle=style[i], dash_capstyle='round', solid_capstyle='round', clip_on=False) # plot race
        line2 = ax.plot(x[i][1], y[i][1], c=c[i], solid_capstyle='round', clip_on=False) # plot penalties
        name = pax.textHorz(x=2, y=y[i][1][-1], s=labels[i], c=c[i], size=10, va ='center', anchor='br') # plot name

        lines.append(line1)
        lines.append(line2)
        names.append(name)

    for pos,colour in position.items():
        pax.textHorz(x=2, y=pos, s=f'{pos}  ', c=colour, size=10, weight='bold', ha='right', va ='center', anchor='br')

    ax.margins(x=0)
    ax.invert_yaxis()
    ax.set_xticks(xtickpos)
    ax.set_xticklabels(xticklabel, size=8)
    ax.set_yticks([])
    plt.tick_params(bottom=False)

    # s
    title = pax.text(x=0, y=2, s='Change in Position', size=16, weight='bold', anchor='tl')
    subtitle = pax.text(x=0, y=0.75, s=session.track, size=10, anchor='tl')
    ax.set_xlabel('Lap', size=12)

    plt.show(block=False)
    
    return fig,ax