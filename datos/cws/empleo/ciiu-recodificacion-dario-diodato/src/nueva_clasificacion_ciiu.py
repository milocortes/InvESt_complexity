import pandas as pd

codificacion = pd.read_csv("recodificacion_ciiu-rev-4_scian_2018.csv")
nombres = pd.read_csv("ciiu-rev-4_nombres.csv")

codificacion = codificacion.query("clasificador=='ciiu'").merge(right=nombres, how="inner", left_on="codigo", right_on="ciiu")
codificacion["ciiu"] = codificacion["ciiu"].apply(lambda x: f"{x:04}")

nueva_codificacion = []
for i in codificacion.codigo_nuevo.unique():
    actividades_integra = codificacion.query(f"codigo_nuevo=={i}")["descripcion_ciiu"].to_list()
    if len(actividades_integra)==1:
        nueva_codificacion.append(
            (i,"".join(actividades_integra),"".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"]),",".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()) )
        )
    else:
        print((i,"/-/".join(actividades_integra),min(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()),",".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list())))
        nueva_codificacion.append(
            (i,"/-/".join(actividades_integra),min(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()),",".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()) )
        )

nueva_codificacion = pd.DataFrame(nueva_codificacion, columns = ["codigo_nuevo", "descripcion_codigo_nuevo", "ciiu_asignado", "actividades_ciiu_integra"])
nueva_codificacion.to_csv("recodificacion_ciiu-rev-4_scian_2018-nombres-correspondencia-ciiu.csv", index = False)
