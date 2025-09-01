import streamlit as st
from core.cube_factory import get_cube


def main():
	# Keep filters visible on the sidebar and use wide layout
	st.set_page_config(page_title="AdventureWorks Analytics", layout="wide", initial_sidebar_state="expanded")
	st.sidebar.title('AdventureWorks Explorer')
	cube = get_cube()


if __name__ == "__main__":
	main()
