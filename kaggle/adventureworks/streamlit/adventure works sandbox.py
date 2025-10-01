import streamlit as st
from core.cube_factory import get_cube, ensure_schema_fig


def main():
	# Landing / overview page
	st.set_page_config(
		page_title="AdventureWorks Analytics • Overview",
		layout="wide",
		initial_sidebar_state="expanded",
	)

	cube = get_cube()

	st.title("AdventureWorks Analytics Demo")
	st.caption("Interactive semantic layer + plotting playground/sandbox powered by cube-alchemy")

	st.markdown(
		"""
		This Streamlit app showcases a lightweight analytics workflow built on top of the
		`cube-alchemy`. A pre-built hypercube is loaded from a
		pickle and then enriched from a YAML model catalog. You can explore the data model, build
		ad‑hoc queries & plots, inspect semantic definitions, and view/persist visualizations.

		Use the left sidebar to apply global filters (they affect all pages). Navigate using the
		page menu to explore each functional area described below.
		"""
	)

	st.markdown("---")
	st.header("Pages Guide")

	col1, col2 = st.columns([1,1])
	with col1:
		st.subheader("1. Schema")
		st.markdown(
			"""
			Visualize the data model as a connected, undirected, acyclic graph.
			You can:
			- Inspect table nodes and their relationships.
			- Review relationship cardinalities (1:1, 1:N, etc.).
			- Build intuition about relationships used when resolving queries.
			"""
		)
		

	with col2:
		fig = ensure_schema_fig(cube)
		if fig is not None:
			st.pyplot(fig, use_container_width=True)
		else:
			st.warning("Schema graph preview unavailable in this session.")

	c1, c2 = st.columns([1,1])
	with c1:
		st.subheader("2. On The Fly")
		st.markdown(
			"""
			Rapidly prototype analyses:
			- Select any combination of **dimensions**, **metrics**, and **derived metrics**.
			- Select from compatible plot types based on your selection shape.
			- Generate a table or visualization instantly.
			- (Optional) Persist a generated plot so it appears on the *Visuals* page.
			"""
		)
		

	with c2:
		st.subheader("3. Definitions")
		st.markdown(
			"""
			Inspect the semantic building blocks in detail:
			- **Dimensions**
			- **Metrics**:
			- **Derived Metrics**
			- **Queries**
			
			This page is useful for auditability & transparency of the analytic layer.
			"""
		)
		

	st.subheader("4. Visuals")
	st.markdown(
		"""
		A gallery of persisted plots. Items appear here when:
		- They are pre-defined in the YAML model (with associated query + plot spec), or
		- You create an ad-hoc query on the *On The Fly* page and click **Save Plot**.

		Each tile renders using the configured Streamlit plot renderer; if a plot fails it falls back to a data table.
		"""
	)
	

	st.markdown("---")
	st.header("How It Works Under The Hood")
	st.markdown(
		"""
		1. The pre-built hypercube object is loaded from a pickle for fast startup (this avoids building the relationships on initialization).
		2. The YAML model catalog is applied to (re)hydrate metrics, derived metrics, queries, and plots.
		3. A Streamlit-specific plot renderer adapts generic plot specs into UI components.
		4. Global filters (sidebar) mutate the session context state so queries automatically pick them up.
		5. Ad-hoc queries are versioned with a UUID-based name and live only on the session.
		"""
	)

	


if __name__ == "__main__":
	main()
