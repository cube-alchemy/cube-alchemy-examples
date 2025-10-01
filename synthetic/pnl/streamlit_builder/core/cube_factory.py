from pathlib import Path
import streamlit as st
from cube_alchemy import Hypercube

from cube_alchemy.plotting.streamlit import StreamlitRenderer
import matplotlib.pyplot as plt

def set_yaml(cube: Hypercube):
    ypath = Path(__file__).parent.parent.parent / "model_catalog.yaml"
    print(f"Setting YAML model catalog from: {ypath}")
    cube.set_yaml_model_catalog(ypath)
    cube.load_from_model_catalog()
    st.session_state.queries = list(reversed(list(cube.queries.keys())))
    #print(ypath)


def get_cube() -> Hypercube:
    #print(get_tables().keys())
    if 'cube' not in st.session_state:
        # Load the cube from pickle file
        pickle_path = Path(__file__).parent.parent.parent / "cube.pkl"
        st.session_state['cube'] = Hypercube.load_pickle(pickle_path, relative_path=False)
        cube = st.session_state['cube']
        cube.set_logger(True)  # enable basic INFO config

        set_yaml(cube)
        
        cube.set_plot_renderer(StreamlitRenderer())

        cube.set_context_state('Default')

        def variation(df, time_dim, value_col, **kwargs):
            # Calculate the percentage change compared to the previous period
            df = df.sort_values(by=time_dim)
            df[f'Previous Period {value_col}'] = df[value_col].shift(1)
            df[f'Variation {value_col} %'] = 100 * (df[value_col] - df[f'Previous Period {value_col}']) / df[f'Previous Period {value_col}']
            df.drop(columns=[f'Previous Period {value_col}'], inplace=True)
            return df

        cube.register_transformer('variation', variation)

    cube = st.session_state['cube']   
    
    return cube

def ensure_schema_fig(cube: Hypercube):
    if 'schema_fig' not in st.session_state:
        try:
            cube.visualize_graph(full_column_names=False, show=False, seed=21)
            st.session_state['schema_fig'] = plt.gcf()
        except Exception:
            st.session_state['schema_fig'] = None
    return st.session_state.get('schema_fig')

def get_cardinallity(cube: Hypercube):
    if 'cardinality' not in st.session_state:
        try:
            st.session_state['cardinality'] = cube.get_cardinalities()
        except Exception:
            st.session_state['cardinality'] = None
    st.write(st.session_state.get('cardinality'))
    return st.session_state.get('cardinality')


