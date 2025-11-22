from streamlit_js_eval import streamlit_js_eval


def get_screen_orientation():

    width = streamlit_js_eval(js_expressions='screen.width')
    height = streamlit_js_eval(js_expressions='screen.height')

    if width > height:
        orientation = 'landscape'
    else:
        orientation = 'portrait'

    return orientation

