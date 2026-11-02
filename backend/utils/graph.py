import plotly
import plotly.graph_objects as go

def build_figure(df, filename, peak_wavelength, peak_absorbance):
    """
    Generate an interactive Plotly spectrum figure with:
    - Glowing blue spectrum line
    - Peak highlight (red marker)
    - Vertical λmax reference line
    - Unified hover tooltip & dark glass theme layout
    """
    x_vals = df['Wavelength'].tolist()
    y_vals = df['Absorbance'].tolist()

    trace_line = go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        line=dict(color='#3b82f6', width=3),
        name='Absorbance',
        hovertemplate='<b>λ:</b> %{x} nm<br><b>Abs:</b> %{y:.4f}<extra></extra>',
    )

    trace_peak = go.Scatter(
        x=[peak_wavelength],
        y=[peak_absorbance],
        mode='markers+text',
        marker=dict(
            color='#ef4444',
            size=14,
            symbol='circle',
            line=dict(color='#ffffff', width=2)
        ),
        text=[f'λmax = {peak_wavelength} nm'],
        textposition='top right',
        textfont=dict(color='#ef4444', size=11, family='Inter, sans-serif'),
        name='Peak (λmax)',
        hovertemplate=(
            f'<b>Peak Wavelength:</b> {peak_wavelength} nm<br>'
            f'<b>Peak Absorbance:</b> {peak_absorbance} AU<extra></extra>'
        ),
    )

    layout = go.Layout(
        title=dict(
            text=f'UV-Vis Absorption Spectrum: {filename}',
            font=dict(size=16, color='#f8fafc', family='Inter, sans-serif'),
            x=0.5
        ),
        template='plotly_dark',
        xaxis=dict(
            title=dict(text='Wavelength (nm)', font=dict(color='#94a3b8')),
            gridcolor='rgba(51,65,85,0.4)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            title=dict(text='Absorbance (AU)', font=dict(color='#94a3b8')),
            gridcolor='rgba(51,65,85,0.4)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter, sans-serif'),
        margin=dict(l=55, r=35, t=65, b=55),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(15,23,42,0.85)',
            bordercolor='rgba(51,65,85,0.6)',
            borderwidth=1
        ),
        annotations=[
            dict(
                x=peak_wavelength,
                y=peak_absorbance,
                xref='x',
                yref='y',
                text=f'Peak: {peak_wavelength} nm ({peak_absorbance} AU)',
                showarrow=True,
                arrowhead=2,
                arrowcolor='#ef4444',
                ax=45,
                ay=-45,
                font=dict(color='#ef4444', size=11, family='Inter, sans-serif'),
                bgcolor='rgba(15,23,42,0.9)',
                bordercolor='#ef4444',
                borderwidth=1
            )
        ]
    )

    fig = go.Figure(data=[trace_line, trace_peak], layout=layout)
    fig.add_vline(
        x=peak_wavelength,
        line_dash='dash',
        line_color='rgba(239,68,68,0.7)',
        line_width=1.5,
        annotation_text='λmax',
        annotation_position='top',
        annotation_font_color='#ef4444',
    )
    return fig
