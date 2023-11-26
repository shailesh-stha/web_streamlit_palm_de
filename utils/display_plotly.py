import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def line_graph(dataframe_1, dataframe_2, band_sequence, time_sequence, band_index, variable_description, variable_unit):
    # Create a Plotly line graph using traces
    fig = go.Figure()
    
    # Filter data points from dataframe_1 and dataframe_2 based on the band_index
    filtered_df1 = dataframe_1[dataframe_1['band_index'].isin(band_sequence)]
    filtered_df2 = dataframe_2[dataframe_2['band_index'].isin(band_sequence)]
    
    fig.add_trace(go.Scatter(x=filtered_df1['band_index'],
                             y=filtered_df1['mean'],
                             name="Base Simulation",))
    
    fig.add_trace(go.Scatter(x=filtered_df2['band_index'],
                             y=filtered_df2['mean'],
                             name="Test Simulation",))
    
    fig.add_vline(x=band_index,
                  line_width=2,
                  line_dash="dash",
                  line_color="green")
    
    # Set the aspect ratio to 3
    fig.update_layout(xaxis_title='Time (Hour)',
                      xaxis = dict(tickmode='array',
                                   tickvals=band_sequence,
                                   ticktext=time_sequence,
                                   showgrid=False,
                                   ticks='outside',
                                   ticklen=5,
                                   tickcolor='grey',
                                   zeroline=False,),
                      yaxis_title= f'{variable_description} [{variable_unit}]',
                      # width=500,
                      height=400,
                      margin=dict(l=20, r=20, t=20, b=20),
                      plot_bgcolor='white',
                      paper_bgcolor="#F2F2F2",)
    
    st.plotly_chart(fig, use_container_width=True, theme="streamlit", )

def bar_graph(dataframe_1, dataframe_2, band_sequence, time_sequence, variable_description, variable_unit, lang_dict):
    # Create a Plotly bar graph using traces
    fig = go.Figure()
    
    # Filter data points from dataframe_1 and dataframe_2 based on the band_index
    filtered_df1 = dataframe_1[dataframe_1['band_index'].isin(band_sequence)]
    filtered_df2 = dataframe_2[dataframe_2['band_index'].isin(band_sequence)]
    
    value_max = int(np.ceil(np.maximum(np.max(filtered_df1['mean']), np.max(filtered_df2['mean']))))
    value_min = int(np.floor(np.minimum(np.min(filtered_df1['mean']), np.min(filtered_df2['mean']))))
    
    # Add bar traces to the figure for each band
    fig.add_trace(go.Bar(x=filtered_df1['band_index'],
                         y=filtered_df1['mean'],
                         name=f"{lang_dict['current_state']}",))
    
    fig.add_trace(go.Bar(x=filtered_df2['band_index'],
                         y=filtered_df2['mean'],
                         name=f"{lang_dict['after_change']}",))
    
    fig.update_layout(height = 450, # width=500,
                      margin=dict(l=20, r=20, t=20, b=20),
                      plot_bgcolor='white',
                      paper_bgcolor="#F2F2F2",
                      legend_x = 0,
                      legend_y = 1,
                      legend=dict(bgcolor='rgba(0,0,0,0)'),
                      legend_font = dict(size=14),
                      )
    
    fig.update_xaxes(title='Zeit',
                     title_font = dict(size=18),
                     tickfont = dict(size=14),
                     tickangle = 90,
                     tickmode = 'array',
                     tickvals = band_sequence,
                     ticktext = time_sequence,
                     )
    
    legend_increase = 2
    if variable_description == "Oberflächentemperatur" or "Surface Temperature":
        legend_increase = 3
    elif variable_description == "Windgeschwindigkeit" or "10-m wind speed":
        legend_increase = 0.1
    elif variable_description == "Nettostrahlung" or "Net radiation flux at the surface":
        legend_increase = 75
    elif variable_description == "Thermal Sensation Index":
        legend_increase = 0

    fig.update_yaxes(title= f'{variable_description} [{variable_unit}]',
                     title_font = dict(size=18),
                     tickfont = dict(size=14),
                     range=[value_min, value_max+legend_increase], # increasement of legend
                     nticks=10,
                     showspikes=True,)
    
    st.plotly_chart(fig, use_container_width=True)

def histogram(variable_data_1, variable_data_2, band_index, time_index, variable_description, variable_unit):
    # read band data in 1d array
    band_data_masked_1 = variable_data_1[band_index, 0, :, :]
    band_data_masked_flatten_1 = band_data_masked_1.flatten()
    band_data_masked_flatten_1 = band_data_masked_flatten_1[~np.isnan(band_data_masked_1.flatten())]
    
    band_data_masked_2 = variable_data_2[band_index, 0, :, :]
    band_data_masked_flatten_2 = band_data_masked_2.flatten()
    band_data_masked_flatten_2 = band_data_masked_flatten_2[~np.isnan(band_data_masked_2.flatten())]
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=band_data_masked_flatten_1,
                               xbins=dict(size=2,),
                               name='Base Simulation',))
    
    fig.add_trace(go.Histogram(x=band_data_masked_flatten_2,
                               xbins=dict(size=2,),
                               name='Test Simulation',))
    
    fig.update_layout(title= f'Histogram at Time:{time_index}',
                      title_x=0.4,
                      xaxis_title = f'{variable_description} [{variable_unit}]',
                      yaxis_title = 'Frequency',
                      # width=500,
                      height=400,
                      margin=dict(l=20, r=20, t=30, b=20),
                      plot_bgcolor='white',
                      paper_bgcolor="#F2F2F2",)
    
    st.plotly_chart(fig, use_container_width=True)