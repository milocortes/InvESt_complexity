import marimo

__generated_with = "0.15.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import altair as alt
    import polars as pl
    import pandas as pd 
    return alt, pd, pl


@app.cell
def _(pl):
    ## Cargamos datos HS2
    df_hs_2d = pl.read_csv("output/hs2_asia_shares_extensivo_intensivo.csv").filter(year=2023)
    df_hs_4d = pl.read_csv("output/asia_shares_extensivo_intensivo.csv").filter(year=2023)

    df_hs_2d = df_hs_2d.with_columns(
        pl.col("export_share_to_usa")*100,
        pl.col("share_on_total_imports")*100,
        pl.col("export_value")/1000_000
    )

    df_hs_4d = df_hs_4d.with_columns(
        pl.col("export_share_to_usa")*100,
        pl.col("share_on_total_imports")*100,
        pl.col("export_value")/1000_000
    )

    ## Subset extensivo 2d
    data_intensivo = df_hs_2d.filter(pl.col("export_rca")>=1.0)

    ## Subset extensivo 2d
    data_extensivo = df_hs_2d.filter(pl.col("export_rca")<1.0)

    ## Subset extensivo 4d
    data_intensivo_4d = df_hs_4d.filter(pl.col("export_rca")>=1.0)

    ## Subset extensivo 4d
    data_extensivo_4d = df_hs_4d.filter(pl.col("export_rca")<1.0)
    return data_extensivo, data_extensivo_4d, data_intensivo, data_intensivo_4d


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# HS2""")
    return


@app.cell
def _(alt, data_intensivo, pd):
    intensivo_share_export_usa = alt.Chart(data_intensivo, title=alt.Title("Industrias del Sector Intensivo (HS2)",subtitle="Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)")).mark_circle().encode(
        alt.X('pci:Q').scale(zero=False, padding=10).title("PCI"),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10).title("Razón con respecto al Total de Importaciones [%]"),
        color=alt.Color('product_hs92_name_1d').title("Cluster"),
        size=alt.Size('export_share_to_usa', scale=alt.Scale(range=[50, 1000])).title("Export Share USA [%]"),
    )

    intensivo_points_text = alt.Chart(data_intensivo).mark_text(
        align='left',
        baseline='middle',
        dx=7, 
    ).encode(
        alt.X('pci:Q').scale(zero=False, padding=10),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10),
        text='product_hs92_name_2d'
    )

    percent_50 = alt.Chart(pd.DataFrame({'y': [50]})).mark_rule(color="red", size = 2).encode(y='y')
    eci_dom = alt.Chart(pd.DataFrame({'x': [-0.19]})).mark_rule(color="black", size = 3).encode(x='x')


    intensivo_share_export_usa + intensivo_points_text + percent_50 + eci_dom
    return eci_dom, intensivo_points_text, percent_50


@app.cell
def _(alt, data_intensivo, eci_dom, intensivo_points_text, percent_50):
    intensivo_export_value = alt.Chart(data_intensivo,  title=alt.Title("Industrias del Sector Intensivo (HS2)",subtitle="Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)")).mark_circle().encode(
        alt.X('pci:Q').scale(zero=False, padding=10).title("PCI"),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10).title("Razón con respecto al Total de Importaciones [%]"),
        color=alt.Color('product_hs92_name_1d').title("Cluster"),
        size=alt.Size('export_value', scale=alt.Scale(range=[50, 2000])).title("Export Value (Million USD)"),
    )

    intensivo_export_value + intensivo_points_text + percent_50 + eci_dom
    return


@app.cell
def _(alt, data_extensivo, eci_dom, percent_50):
    extensivo_share_export_usa = alt.Chart(data_extensivo,  title=alt.Title("Industrias del Sector Extensivo (HS2)",subtitle="Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)")).mark_circle().encode(
        alt.X('pci:Q').scale(zero=False, padding=10).title("PCI"),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10).title("Razón con respecto al Total de Importaciones [%]"),
        color=alt.Color('product_hs92_name_1d').title("Cluster"),
        size=alt.Size('export_share_to_usa', scale=alt.Scale(range=[50, 1000])).title("Export Share USA [%]"),
    )

    extensivo_points_text = alt.Chart(data_extensivo).mark_text(
        align='left',
        baseline='middle',
        dx=7, 
    ).encode(
        alt.X('pci:Q').scale(zero=False, padding=10),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10),
        text='product_hs92_name_2d'
    )

    extensivo_share_export_usa + extensivo_points_text + percent_50 + eci_dom
    return (extensivo_points_text,)


@app.cell
def _(alt, data_extensivo, eci_dom, extensivo_points_text, percent_50):
    extensivo_export_value = alt.Chart(data_extensivo, title=alt.Title("Industrias del Sector Extensivo (HS2)",subtitle="Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)")).mark_circle().encode(
        alt.X('pci:Q').scale(zero=False, padding=10).title("PCI"),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10).title("Razón con respecto al Total de Importaciones [%]"),
        color=alt.Color('product_hs92_name_1d').title("Cluster"),
        size=alt.Size('export_value', scale=alt.Scale(range=[50, 2000])).title("Export Value (Million USD)"),
    )

    extensivo_export_value + extensivo_points_text + percent_50 + eci_dom
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# HS4""")
    return


@app.cell
def _(alt, data_intensivo_4d, eci_dom, pd, pl):
    plot_data_intensivo_4d = alt.Chart(data_intensivo_4d, title=alt.Title("Industrias del Sector Intensivo (HS4)",subtitle="Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)")).mark_circle(size = 400).encode(
        alt.X('pci:Q').scale(zero=False, padding=10).title("PCI"),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10).title("Razón con respecto al Total de Importaciones [%]"),
        color=alt.Color('product_hs92_name_1d',
              scale=alt.Scale(
                  domain = ["Agriculture", "Chemicals", "Machinery", "Metals", "Minerals", "Stone", "Textiles", "Electronics"],
                  range = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]
              )
                       ).title("Cluster"),
    )

    plot_data_intensivo_4d_points_text = alt.Chart(
        data_intensivo_4d.filter(
            (pl.col("share_on_total_imports")>40) & 
            (pl.col("pci")>-0.19)
        )
    ).mark_text(
        align='left',
        baseline='middle',
        dx=20, 
        size = 8
    ).encode(
        alt.X('pci:Q').scale(zero=False, padding=10),
        alt.Y('share_on_total_imports:Q').scale(zero=False, padding=10),
        text='product_hs92_name_4d'
    )

    percent_40 = alt.Chart(pd.DataFrame({'y': [40]})).mark_rule(color="red", size = 2).encode(y='y')

    plot_data_intensivo_4d  + plot_data_intensivo_4d_points_text + percent_40 + eci_dom
    return


@app.cell
def _(data_intensivo_4d, pl):
    data_intensivo_4d.filter(
            (pl.col("share_on_total_imports")>40) & 
            (pl.col("pci")>-0.19)
        )
    return


@app.cell
def _(data_intensivo):
    data_intensivo
    return


@app.cell
def _(data_extensivo):
    data_extensivo

    return


@app.cell
def _(data_intensivo_4d):
    data_intensivo_4d
    return


@app.cell
def _(data_extensivo_4d):
    data_extensivo_4d
    return


if __name__ == "__main__":
    app.run()
