# BSD 3-Clause License

# Copyright (c) 2022- , Colin Xu <colin.xu@gmail.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os, json, itertools
import altair as alt
import datetime as dt
import pandas as pd

# Overall layout
GRAPH_WIDTH = 800
GRAPH_BAR_HEIGHT = 10
GRAPH_BAR_SPACE = 35
GRAPH_BAR_OPACITY = 0.8

# Shift milestone text below marker, date lower
EVENT_DESC_OFFSET_X = 5
EVENT_DESC_OFFSET_Y = 15
EVENT_DATE_DESC_OFFSET_X = 5
EVENT_DATE_DESC_OFFSET_Y = 24

# Only plot 5 quarters: [-1, +4]
RANGE_START = (pd.Timestamp.today() - pd.tseries.offsets.QuarterEnd(2) + pd.Timedelta(days = 1)).strftime('%Y-%m-%d')
RANGE_END = (pd.Timestamp.today() + pd.tseries.offsets.QuarterEnd(4)).strftime('%Y-%m-%d')

# Chart background and text color
CHART_COLOR_BG = '#E7EFF1'
CHART_COLOR_FG = '#000000'
TODAY_COLOR = '#43C59E'

# Chart header (quarter & month) color
QUARTER_COLOR_BG = '#000000'
QUARTER_COLOR_FG = '#FFFFFF'
MONTH_COLOR_BG = itertools.cycle(['#A3B0BB', '#60696B'])
MONTH_COLOR_FG = '#000000'

class ProgramChart():
    head_bar_list_q = []
    head_bar_list_m = []
    chart_today = None
    chart_header = []
    chart_program = []

    def __init__(self, ps):
        self.ps = ps
        self.name = ps.description

    def PrepareQuarterHeader(self):
        self.head_bar_list_q = []
        for quarter in pd.date_range(RANGE_START, RANGE_END, freq = 'QS'):
            q_start = quarter.strftime('%Y-%m-%d')
            q_end = (quarter + pd.tseries.offsets.QuarterEnd(1)).strftime('%Y-%m-%d')
            q_entry = {'Program': 'Quarter',
                       'Index': 0,
                       'Start': pd.to_datetime(q_start),
                       'End': pd.to_datetime(q_end),
                       'BGColor': QUARTER_COLOR_BG,
                       'FGColor': QUARTER_COLOR_FG,
                       'Description': str(quarter.year) + 'Q' + str(quarter.quarter)
                       }
            self.head_bar_list_q.append(q_entry)

    def PrepareMonthHeader(self):
        self.head_bar_list_m = []
        for month in pd.date_range(RANGE_START, RANGE_END, freq = 'MS'):
            m_start = month.strftime('%Y-%m-%d')
            m_end = (month + pd.tseries.offsets.MonthEnd(1)).strftime('%Y-%m-%d')
            m_entry = {'Program': 'Month',
                    'Index': 1,
                    'Start': pd.to_datetime(m_start),
                    'End': pd.to_datetime(m_end),
                    'BGColor': next(MONTH_COLOR_BG),
                    'FGColor': MONTH_COLOR_FG,
                    'Description': month.strftime('%m')}
            self.head_bar_list_m.append(m_entry)

    def PrepareChartHeader(self):
        self.PrepareQuarterHeader()
        self.PrepareMonthHeader()

    def PlotMonthQuarterBlock(self):
        self.chart_header.append(
            alt.Chart(pd.DataFrame(self.head_bar_list_q + self.head_bar_list_m)).mark_bar(
                    opacity = GRAPH_BAR_OPACITY,
                    cornerRadius = 5
                ).encode(
                x = alt.X('Start',
                        scale = alt.Scale(domain = [RANGE_START, RANGE_END]),
                        axis = alt.Axis(title = self.name,
                                        labelAngle = 0,
                                        format = ('%m'),
                                        tickCount = {'interval': 'month', 'step': 1},
                                        orient = 'top',
                                        labels = False,
                                        ticks = False,
                                        ),
                        timeUnit = 'yearmonth',
                    ),
                x2 = 'End',
                y = alt.Y('Index:N',
                        axis = alt.Axis(title = None,
                                        labels = False,
                                        ticks = False
                                        ),
                        sort = alt.SortField(field = 'Index', order = 'ascending')
                        ),
                color = alt.Color('BGColor:N', scale = None)
            ).properties(width = GRAPH_WIDTH)
        )

    def PlotQuarterText(self):
        self.chart_header.append(
            alt.Chart(pd.DataFrame(self.head_bar_list_q)).mark_text(dx = 80, align = 'center', color = QUARTER_COLOR_FG).encode(
                      x = 'Start',
                      x2 = 'End',
                      y = 'Index:N',
                      detail = 'site:N',
                      text = alt.Text('Description')
                      )
        )

    def PlotMonthText(self):
        self.chart_header.append(
            alt.Chart(pd.DataFrame(self.head_bar_list_m)).mark_text(dx = 25, align = 'center', color = MONTH_COLOR_FG).encode(
                      x = 'Start',
                      x2 = 'End',
                      y = 'Index:N',
                      detail = 'site:N',
                      text = alt.Text('Description')
                      )
        )

    def PlotChartToday(self):
        self.chart_today = alt.Chart(pd.DataFrame({'Date': [pd.Timestamp.today().strftime('%Y-%m-%d')], 'Color': [TODAY_COLOR]})
                      ).mark_rule(strokeWidth = 2, strokeDash=[5, 3]).encode(
                            x = alt.X('Date:T', scale = alt.Scale(domain = [RANGE_START, RANGE_END])),
                            color = alt.Color('Color:N', scale = None)
                            ).properties(width = GRAPH_WIDTH)

    def PlotChartHeader(self):
        self.PlotMonthQuarterBlock()
        self.PlotQuarterText()
        self.PlotMonthText()
        self.PlotChartToday()

    def PlotProgramPhase(self):
        legend_domain = []
        legend_range = []
        for p in self.ps.phases:
            legend_domain.append(p['Description'])
            legend_range.append(p['BGColor'])

        self.chart_program.append(
            alt.Chart(pd.DataFrame(self.ps.program_bar_range_list)).mark_bar(
                    opacity = GRAPH_BAR_OPACITY,
                    size = GRAPH_BAR_HEIGHT,
                    cornerRadius = 5
                ).encode(
                x = alt.X('Start',
                        scale = alt.Scale(domain = [RANGE_START, RANGE_END]),
                        axis = alt.Axis(title = '',
                                        labelAngle=0,
                                        format = ('%m'),
                                        tickCount = {'interval': 'month', 'step': 1},
                                        orient = 'top',
                                        labels = False,
                                        ticks = False,
                                        ),
                        ),
                x2 = 'End',
                y = alt.Y('Index:N',
                        axis = alt.Axis(title = None, ticks = False, labels = False),
                        sort = alt.EncodingSortField(field = 'Index', order = 'ascending'),
                        ),
                color = alt.Color('Type:N',
                                  title = 'Phase',
                                  scale = alt.Scale(domain = legend_domain, range = legend_range),
                                  legend = alt.Legend(orient = 'right')
                                  ),
            ).properties(width = GRAPH_WIDTH, height = (GRAPH_BAR_SPACE * len(self.ps.schedule_data['Data'])))
        )

    def PlotProgramName(self):
        self.chart_program.append(
            alt.Chart(pd.DataFrame(self.ps.program_bar_name_list)).mark_text(dx = -5, align = 'right').encode(
                x = alt.value(0),
                y = alt.Y('Index:N',
                        axis = alt.Axis(title = None, ticks = False, labels = False),
                        sort = alt.EncodingSortField(field = 'Index', order = 'ascending'),
                        ),
                color = alt.Color('FGColor:N', scale = None, legend = None),
                text = 'Program:N'
            ).properties(width = GRAPH_WIDTH, height = (GRAPH_BAR_SPACE * len(self.ps.schedule_data['Data'])))
        )

    def PlotProgramPhaseDescription(self):
        self.chart_program.append(
            alt.Chart(pd.DataFrame(self.ps.program_bar_range_list)).mark_text(dx = 5, align = 'left').encode(
                x = alt.X('Start', scale = alt.Scale(domain=[RANGE_START, RANGE_END])),
                y = alt.Y('Index:N',
                        axis = alt.Axis(title = None, ticks = False, labels = False),
                        sort = alt.EncodingSortField(field = 'Index', order = 'ascending'),
                        ),
                color = alt.Color('FGColor:N', scale = None, legend = None),
                text = 'Description:N'
            ).properties(width = GRAPH_WIDTH, height = (GRAPH_BAR_SPACE * len(self.ps.schedule_data['Data'])))
        )

    def PlotProgramEvent(self):
        legend_domain = []
        legend_range = []
        for e in self.ps.events:
            legend_domain.append(e['Description'])
            legend_range.append(e['BGColor'])
        self.chart_program.append(
            alt.Chart(pd.DataFrame(self.ps.program_bar_event_list)).mark_point(filled = True, size = 100, yOffset = 10).encode(
                x = alt.X('Date',
                          scale = alt.Scale(domain=[RANGE_START, RANGE_END])),
                y = alt.Y('Index:O',
                          axis = alt.Axis(title = None, ticks = False, labels = False),
                          sort = alt.EncodingSortField(field = 'Index', order = 'ascending'),
                          ),
                shape = alt.Shape('Type:N',
                                  title = 'Milestone',
                                  scale = alt.Scale(domain = legend_domain, range = ['triangle-up'])),
                color = alt.Color('Type:N',
                                  title = 'Milestone',
                                  scale = alt.Scale(domain = legend_domain, range = legend_range),
                                  legend = alt.Legend(orient = 'right')
                                  ),
            ).properties(width = GRAPH_WIDTH, height = (GRAPH_BAR_SPACE * len(self.ps.schedule_data['Data'])))
        )

    def PlotProgramEventDescription(self):
        self.chart_program.append(
            alt.Chart(pd.DataFrame(self.ps.program_bar_event_list)).mark_text(dx = EVENT_DESC_OFFSET_X, dy = EVENT_DESC_OFFSET_Y, align = 'left').encode(
                x = alt.X('Date', scale = alt.Scale(domain = [RANGE_START, RANGE_END])),
                y = alt.Y('Index:N',
                        axis = alt.Axis(title = None, ticks = False, labels = False),
                        sort = alt.EncodingSortField(field = 'Index', order = 'ascending'),
                        ),
                color = alt.Color('FGColor:N', scale = None, legend = None),
                text = 'Description'
            ).properties(width = GRAPH_WIDTH, height = (GRAPH_BAR_SPACE * len(self.ps.schedule_data['Data'])))
        )

    def PlotProgramEventDate(self):
        self.chart_program.append(
            alt.Chart(pd.DataFrame(self.ps.program_bar_event_list)).mark_text(dx = EVENT_DATE_DESC_OFFSET_X, dy = EVENT_DATE_DESC_OFFSET_Y, align = 'left').encode(
                x = alt.X('Date', scale = alt.Scale(domain=[RANGE_START, RANGE_END])),
                y = alt.Y('Index:N',
                        axis = alt.Axis(title = None, ticks = False, labels = False),
                        sort = alt.EncodingSortField(field = 'Index', order = 'ascending'),
                        ),
                color = alt.Color('FGColor:N', scale = None, legend = None),
                text = 'Date_Short'
            ).properties(width = GRAPH_WIDTH, height = (GRAPH_BAR_SPACE * len(self.ps.schedule_data['Data'])))
        )

    def PlotChartBody(self):
        self.PlotProgramPhase()
        self.PlotProgramName()
        self.PlotProgramPhaseDescription()
        self.PlotProgramEvent()
        self.PlotProgramEventDescription()
        self.PlotProgramEventDate()

    def PlotShow(self):
        alt.renderers.enable('altair_viewer')
        alt.vconcat(alt.layer(
                        self.chart_header[0],
                        self.chart_header[1],
                        self.chart_header[2],
                        self.chart_today
                        ),
                    alt.layer(
                        self.chart_program[0],
                        self.chart_program[1],
                        self.chart_program[2],
                        self.chart_program[3],
                        self.chart_program[4],
                        self.chart_program[5],
                        self.chart_today
                        ).resolve_scale(
                            color = 'independent',
                            shape = 'independent'
                        )
            ).configure(
                background = CHART_COLOR_BG
            ).configure_concat(
                spacing = 0
            ).show()

class ProgramSchedule():
    schedule_data = json.dumps({'key': 1})
    description = 'Program Details'
    phases = []
    events = []
    program_bar_name_list = []
    program_bar_range_list = []
    program_bar_event_list = []

    def __init__(self, name):
        self.name = name

    def ParseDataFromJSON(self, file):
        with open(file) as f:
            try:
                self.schedule_data = json.load(f)
                if 'Data' not in self.schedule_data:
                    print('JSON %s doesn\'t have valid data for schedule and event' %(file))
                    exit()
                if 'Phase_List' not in self.schedule_data:
                    print('JSON %s doesn\'t have valid Phase definition' %(file))
                    exit()
                if 'Event_List' not in self.schedule_data:
                    print('JSON %s doesn\'t have valid Event definition' %(file))
                    exit()
                if 'Description' in self.schedule_data:
                    self.description = self.schedule_data['Description']
            except ValueError as err:
                print('Invalid JSON for %s' %(file))
                exit()

        print(self.description, 'Loaded from JSON')

    def PreparePhaseList(self):
        self.phases = []
        for phase_def in self.schedule_data['Phase_List']:
            self.phases.append({'Type': phase_def['Type'], 'Description': phase_def['Description'], 'BGColor': phase_def['BGColor'], 'FGColor': phase_def['FGColor']})

    def PrepareEventList(self):
        self.events = []
        for event_def in self.schedule_data['Event_List']:
            self.events.append({'Type': event_def['Type'], 'Description': event_def['Description'], 'BGColor': event_def['BGColor'], 'FGColor': event_def['FGColor']})

    def ProcessProgramDetails(self):
        self.program_bar_name_list = []
        self.program_bar_range_list = []
        self.program_bar_event_list = []

        for program_data in self.schedule_data['Data']:
            # Prepare all program name to be shown on y-axis
            self.program_bar_name_list.append({'Program': program_data['Program'], 'Index': program_data['Index'], 'FGColor': CHART_COLOR_FG})

            # Prepare phase bar
            if 'Phase' in program_data:
                for program_phase in program_data['Phase']:
                    # Decide current phase type
                    unsupported = True
                    for p in self.phases:
                        if (p['Type'] == program_phase['Type']):
                            unsupported = False
                            break
                    if (unsupported):
                        print('Unsupported Phase type %d for %s' %(program_phase['Type'], program_data['Program']))
                        exit()

                    entry = {'Program': program_data['Program'],
                             'Index': program_data['Index'],
                             'Type': p['Description'], # Use description as Type for legend label
                             'Start': ((pd.to_datetime(RANGE_START)) if (pd.to_datetime(program_phase['Start']) < pd.to_datetime(RANGE_START)) else (pd.to_datetime(program_phase['Start']))) if (program_phase['Start'] != '') else (pd.to_datetime(RANGE_START)),
                             'End' : ((pd.to_datetime(RANGE_END)) if (pd.to_datetime(program_phase['End']) > pd.to_datetime(RANGE_END)) else (pd.to_datetime(program_phase['End']))) if (program_phase['End'] != '') else (pd.to_datetime(RANGE_END)),
                             'BGColor': p['BGColor'],
                             'FGColor': p['FGColor'],
                             'Description': ''
                            }
                    if (('End_Today' in program_phase) and program_phase['End_Today']):
                        entry['End'] = pd.to_datetime(pd.Timestamp.today().strftime('%Y-%m-%d'))

                    # Hide phase description
                    if (not program_phase['Hide_Description']):
                        entry['Description'] = (p['Description'] + str(program_phase['Additional Info'])) if ('Additional Info' in program_phase) else (p['Description'])
                    self.program_bar_range_list.append(entry)

            # Prepare event marker
            if 'Event' in program_data:
                for program_event in program_data['Event']:
                    # Decide current event type
                    unsupported = True
                    for e in self.events:
                        if (e['Type'] == program_event['Type']):
                            unsupported = False
                            break
                    if (unsupported):
                        print('Unsupported Event type %d for %s' %(program_event['Type'], program_data['Program']))
                        exit()

                    entry = {'Program': program_data['Program'],
                             'Index': program_data['Index'],
                             'Type': e['Description'], # Use description as Type for legend label
                             'Date': pd.to_datetime(program_event['Date']),
                             'BGColor': e['BGColor'],
                             'FGColor': e['FGColor'],
                             'Description': (e['Description'] + str(program_event['Additional Info'])) if ('Additional Info' in program_event) else (e['Description']),
                             'Date_Short': str(pd.to_datetime(program_event['Date']).strftime('%m/%d') + ((str(program_event['Additional Date Info'])) if ('Additional Date Info' in program_event) else ('')))
                            }
                    self.program_bar_event_list.append(entry)

def PlotGantt(name, json_file):
    ps = ProgramSchedule(name)
    if (os.path.isfile(json_file)):
        ps.ParseDataFromJSON(json_file)
        ps.PreparePhaseList()
        ps.PrepareEventList()
        ps.ProcessProgramDetails()

        pc = ProgramChart(ps)
        pc.PrepareChartHeader()
        pc.PlotChartHeader()
        pc.PlotChartBody()
        pc.PlotShow()
    else:
        print('No program JSON file provided')
