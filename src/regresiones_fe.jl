using DataFrames, CSV, FixedEffectModels, GLM, RegressionTables

### Cargamos los datos
complexity_zm = DataFrame(CSV.File("/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/src/regresiones_crecimiento.csv"))

RegressionTables.default_breaks(render::AbstractRenderType) = [0.01, 0.05, 0.1]

### RCA GROWTH
reg_growth_rca_uno = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca +
                    fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))

reg_growth_rca_dos = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_input_presence + 
                    fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))

reg_growth_rca_tres = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_input_presence_similarity +
                    fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))

reg_growth_rca_cuatro = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence + 
                    fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))

reg_growth_rca_cinco = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence_similarity +
                    fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))                                        


reg_growth_rca_seis = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca +  arcsinh_coempleo_presence_continua + 
                    fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))                                        

reg_growth_rca_siete = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity+
                    fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))    

reg_growth_rca_ocho = reg(complexity_zm, 
                    @formula(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity+
                    arcsinh_coempleo_calificado_presence +fe(zm) + fe(actividad)), Vcov.cluster(:zm, :actividad))    

regtable(
    reg_growth_rca_uno, reg_growth_rca_dos, reg_growth_rca_tres, reg_growth_rca_cuatro, reg_growth_rca_cinco, reg_growth_rca_seis, reg_growth_rca_siete;
    render = AsciiTable(),
    labels = Dict(
        "apariciones" => "Apariciones",
        "desapariciones" => "Desapariciones",
        "zm" => "Zona Metropolitana",
        "actividad" => "Actividad CIIU",
        "arcsinh_density"  => "Density",
        "arcsinh_rca" => "RCA",
        "arcsinh_output_presence" => "Output Presence",
        "arcsinh_input_presence" => "Input Presence",
        "arcsinh_coempleo_presence_continua" => "Co-empleo",
        "arcsinh_input_presence_similarity" => "Input Presence Similarity",
        "growth_rca_arcsinh" => "Crecimiento RCA"
    ),
    regression_statistics = [
        Nobs => "Obs.",
        R2,
        R2Within,
        PseudoR2 => "Pseudo-R2",
    ]
)

regtable(
    reg_growth_rca_uno, reg_growth_rca_dos, reg_growth_rca_tres, reg_growth_rca_cuatro, reg_growth_rca_cinco, reg_growth_rca_seis, reg_growth_rca_siete;
    render = LatexTable(),
    labels = Dict(
        "apariciones" => "Apariciones",
        "desapariciones" => "Desapariciones",
        "zm" => "Zona Metropolitana",
        "actividad" => "Actividad CIIU",
        "arcsinh_density"  => "Density",
        "arcsinh_rca" => "RCA",
        "arcsinh_output_presence" => "Output Presence",
        "arcsinh_input_presence" => "Input Presence",
        "arcsinh_coempleo_presence_continua" => "Co-empleo",
        "arcsinh_input_presence_similarity" => "Input Presence Similarity",
        "arcsinh_output_presence_similarity" => "Output Presence Similarity",
        "growth_rca_arcsinh" => "Crecimiento RCA"
    ),
    regression_statistics = [
        Nobs => "Obs.",
        R2,
        R2Within,
        PseudoR2 => "Pseudo-R2",
    ], 
    file="rca_growth.tex"

)

#groups = ["Región:", "Todo" => 2:3, "Norte" => 4:5, "Centro-Norte" => 6:7, "Centro" => 8:9, "Sur" => 10:11],


### Apariciones

apariciones_uno = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm),
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca +
                    fe(zm) + fe(actividad)))

apariciones_dos = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm), 
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_input_presence + 
                    fe(zm) + fe(actividad)))

apariciones_tres = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm), 
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_input_presence_similarity +
                    fe(zm) + fe(actividad)))

apariciones_cuatro = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm), 
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence + 
                    fe(zm) + fe(actividad)))

apariciones_cinco = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm), 
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence_similarity +
                    fe(zm) + fe(actividad)))                                        


apariciones_seis = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm), 
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca +  arcsinh_coempleo_presence_continua + 
                    fe(zm) + fe(actividad)))                                        

apariciones_siete = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm), 
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity+
                    fe(zm) + fe(actividad)))                                        

apariciones_ocho = reg(filter(row -> row.rca_2015 < 0.05, complexity_zm), 
                    @formula(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence  + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity+
                    arcsinh_coempleo_calificado_presence + fe(zm) + fe(actividad)))  

### Desapariciones

desapariciones_uno = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm),
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca +
                    fe(zm) + fe(actividad)))

desapariciones_dos = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm), 
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_input_presence + 
                    fe(zm) + fe(actividad)))

desapariciones_tres = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm), 
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_input_presence_similarity +
                    fe(zm) + fe(actividad)))

desapariciones_cuatro = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm), 
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence + 
                    fe(zm) + fe(actividad)))

desapariciones_cinco = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm), 
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence_similarity +
                    fe(zm) + fe(actividad)))                                        


desapariciones_seis = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm), 
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca +  arcsinh_coempleo_presence_continua + 
                    fe(zm) + fe(actividad)))                                        

desapariciones_siete = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm), 
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity+
                    fe(zm) + fe(actividad)))                                        

desapariciones_ocho = reg(filter(row -> row.rca_2015 > 0.2, complexity_zm), 
                    @formula(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity+
                    arcsinh_coempleo_calificado_presence + fe(zm) + fe(actividad)))   

regtable(
    apariciones_uno, apariciones_dos, apariciones_tres, apariciones_cuatro, apariciones_cinco, apariciones_seis, apariciones_siete,apariciones_ocho, 
    desapariciones_uno, desapariciones_dos, desapariciones_tres, desapariciones_cuatro, desapariciones_cinco, desapariciones_seis, desapariciones_siete, desapariciones_ocho;
    render = AsciiTable(),
    labels = Dict(
        "apariciones" => "Apariciones",
        "desapariciones" => "Desapariciones",
        "zm" => "Zona Metropolitana",
        "actividad" => "Actividad CIIU",
        "arcsinh_density"  => "Density",
        "arcsinh_rca" => "RCA",
        "arcsinh_output_presence" => "Output Presence",
        "arcsinh_input_presence" => "Input Presence",
        "arcsinh_coempleo_presence_continua" => "Co-empleo",
        "arcsinh_input_presence_similarity" => "Input Presence Similarity",
        "arcsinh_output_presence_similarity" => "Output Presence Similarity",
        "arcsinh_coempleo_calificado_presence"=> "Co-empleo Calificado"
    ),
    regression_statistics = [
        Nobs => "Obs.",
        R2,
        R2Within,
        PseudoR2 => "Pseudo-R2",
    ]
)

regtable(
    apariciones_uno, apariciones_dos, apariciones_tres, apariciones_cuatro, apariciones_cinco, apariciones_seis, apariciones_siete; 
    render = LatexTable(),
    labels = Dict(
        "apariciones" => "Apariciones",
        "desapariciones" => "Desapariciones",
        "zm" => "Zona Metropolitana",
        "actividad" => "Actividad CIIU",
        "arcsinh_density"  => "Density",
        "arcsinh_rca" => "RCA",
        "arcsinh_output_presence" => "Output Presence",
        "arcsinh_input_presence" => "Input Presence",
        "arcsinh_coempleo_presence_continua" => "Co-empleo",
        "arcsinh_input_presence_similarity" => "Input Presence Similarity",
        "arcsinh_output_presence_similarity" => "Output Presence Similarity",
        "arcsinh_coempleo_calificado_presence"=> "Co-empleo Calificado",
    ),
    regression_statistics = [
        Nobs => "Obs.",
        R2,
        R2Within,
        PseudoR2 => "Pseudo-R2",
    ]
    , file="apariciones.tex"
)

regtable(
    desapariciones_uno, desapariciones_dos, desapariciones_tres, desapariciones_cuatro, desapariciones_cinco, desapariciones_seis, desapariciones_siete;
    render = LatexTable(),
    labels = Dict(
        "apariciones" => "Apariciones",
        "desapariciones" => "Desapariciones",
        "zm" => "Zona Metropolitana",
        "actividad" => "Actividad CIIU",
        "arcsinh_density"  => "Density",
        "arcsinh_rca" => "RCA",
        "arcsinh_output_presence" => "Output Presence",
        "arcsinh_input_presence" => "Input Presence",
        "arcsinh_coempleo_presence_continua" => "Co-empleo",
        "arcsinh_input_presence_similarity" => "Input Presence Similarity",
        "arcsinh_output_presence_similarity" => "Output Presence Similarity"
    ),
    regression_statistics = [
        Nobs => "Obs.",
        R2,
        R2Within,
        PseudoR2 => "Pseudo-R2",
    ]
    , file="desapariciones.tex"
)
