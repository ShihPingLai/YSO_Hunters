#!/usr/bin/csh
# ======================================================
# This program is a pipeline for cloud catalog
# MCCloud: CHA_II, LUP_I, LUP_III, LUP_IV, OPH, SER, PER
#
# Pipeline.csh [GP dir] [Add UKIDSS] [dimension] [cube size] [sigma] [bond] [refD] [GP only]"

# [GP_dir]:      directory that stores galaxy probability (absolute_path_to_dir or 'default')"
# [Add UKIDSSj]: add UKIDSS data or not (yes/no)"
# [dimension]:   dimension of magnitude space (for now only '6')"
# [cube size]:   length of multi-d cube in magnitude unit"
# [sigma]:       standard deviation for gaussian dist. in magnitude"
# [bond]:        boundary for gaussian smooth radius (in magnitude)"
# [refD]:        reference dimension which to modulus other dimension to"
# [GP only]:     option to only calculate GP and skip all process before [yes/no]"
# Latest update JordanWu 2020/12/21
# ======================================================

# Variables
# ======================================================
# Help for input arguments
if ( ${#argv} != 8 ) then
    echo "\n\tExample: Pipeline.csh [GP dir] [Add UKIDSS] [dimension] [cube size] [sigma] [bond] [refD] [GP only]"
    echo "\t[GP_dir]: to the directory which contains the directory that stores galaxy probability (absolute_path_to_dir or 'default')"
    echo "\t[Add UKIDSS]: add UKIDSS data or not (yes/no)"
    echo "\t[dimension]: dimension of magnitude space (for now only '6')"
    echo "\t[cube size]: length of multi-d cube in magnitude unit (in magnitude)"
    echo "\t[sigma]: standard deviation for gaussian dist. (in magnitude)"
    echo "\t[bond]: boundary for gaussian smooth radius (in magnitude)"
    echo "\t[refD]: reference dimension which to modulus other dimension to (integeter only)"
    echo "\t[GP only]: option to only calculate GP and skip all process before [yes/no]"
    echo "\t*** Warning: This program must be executed in directory which also stores galaxy probability ... ***"
    echo "\t*** Warning: UKIDSS data here only contains data with mag < 11.5, and fake qua, psf labels are assigned ...***"
    echo "\t*** Warning: If you are using BD method, please check source code if the boundary array is correct ... ***"
    echo "\t*** Process before GP method: Catalog_transformation, Star_removal, Extinction_correction, Find_saturate ... ***\n"
    exit
endif

# table, directory, and logfile
set YSO_table='/mazu/users/jordan/YSO_Project/YSO_Hunters_Table'
set logfile='term.out'

# command line argument
set UKIDSS=${2}
set dim=${3}
set cube=${4}
set sigma=${5}
set bond=${6}
set refD=${7}
set only_GP=${8}

# Set GP directory
if ( ${1} == default ) then
    set GP_dir='/mazu/users/jordan/YSO_Project/SEIP_GP_Bound'
else
    set GP_dir=${1}
endif
echo "\nGP_dir: ${GP_dir}"

# Generate Full Inp bands
set i = 0
set full_inp = ""
while ($i < $dim)
   set full_inp = "${full_inp}${i}"
   @ i++
end

# Cloud indice and ukidss observation indicator
set indice=(1 2 3 4 5 6 7)
set clouds=(CHA_II LUP_I LUP_III LUP_IV OPH SER PER)

if ( ${UKIDSS} == yes ) then
    # for new added UKIDSS catalog
    set ukidss_obs=(0 0 0 0 1 1 1)
else
    #for original Hsieh's classification
    set ukidss_obs=(0 0 0 0 0 0 0)
endif

# Main Program
# ======================================================

# Setup
if ( ${UKIDSS} == yes ) then
    set par_dir=Cloud_Classification_GPM_${dim}D_Diag_BD_UKIDSS
else
    set par_dir=Cloud_Classification_GPM_${dim}D_Diag_BD_ORIGINAL
endif

if ( ! -d ${par_dir} ) mkdir ${par_dir} && cd ${par_dir}
set out_dir="${dim}D_bin${cube}_sigma${sigma}_bond${bond}_refD${refD}"
if ( ! -d ${out_dir} ) mkdir ${out_dir} && cd ${out_dir}

# Run for all clouds
foreach i (${indice})

    # Initialization
    set cloud=${clouds[${i}]}
    echo "\nInitializing ${cloud} ..."

    # Only GP method
    if ( ${only_GP} == yes ) then
        if ( ! -d ${cloud} ) mkdir ${cloud} && cd ${cloud}
        if ( -f ${logfile} ) rm ${logfile}
        echo "Transforming catalog format ... [SKIP]"
        echo "Removing stars ... [SKIP]"
        echo "Correcting extinction ... [SKIP]"
        echo "Finding saturate ... [SKIP]"
    # Full classification process
    else
        # Add artificial quality label and Start Preset Procedure
        if ( ! -d ${cloud} ) mkdir ${cloud} && cd ${cloud}
        if ( -f ${logfile} ) rm ${logfile}
        /usr/bin/cp -f ${YSO_table}/All_Converted_Catalog/SPITZER/catalog-${cloud}-HREL.tbl catalog-${cloud}-HREL.tbl | tee -a ${logfile}
        # WO/WI UKIDSS observation
        echo "Adding magnitudes ..."
        if ( ${ukidss_obs[${i}]} == 0 ) then
            Add_Mag_To_C2D_Full.py catalog-${cloud}-HREL.tbl catalog-${cloud}-HREL-Add_Mag.tbl | tee -a ${logfile}
            TF_From_2MASS_To_UKIDSS_System.py catalog-${cloud}-HREL-Add_Mag.tbl catalog-${cloud}-HREL-Add_Mag-TF_UKIDSS.tbl | tee -a ${logfile}
            echo "Adding artificial quality labels ..."
            Add_Mag_Qua_JHK_UKIDSS.py catalog-${cloud}-HREL-Add_Mag-TF_UKIDSS.tbl default N A_fake | tee -a ${logfile}
            Add_Mag_Qua_JHK_UKIDSS.py catalog-${cloud}-HREL-Add_Mag-TF_UKIDSS-Add_JHK_Qua.tbl default U A_fake | tee -a ${logfile}
            echo "Start setting neeed presets ..."
            SOP_Execution_Preset.py catalog-${cloud}-HREL-Add_Mag-TF_UKIDSS-Add_JHK_Qua-Add_JHK_Qua.tbl ${cloud} Self_made | tee -a ${logfile}
        else if ( ${ukidss_obs[${i}]} == 1 ) then
            # Different UKIDSS observation programs
            if ( ${cloud} == OPH ) then
                set ukidss_catalog="${YSO_table}/All_UKIDSS_Catalog/UKIDSS_OBSERVATION/DR11PLUS/UKIDSS_GCS/UKIDSS_GCS_${cloud}.csv"
                set header=13
            else if ( ${cloud} == SER ) then
                set ukidss_catalog="${YSO_table}/All_UKIDSS_Catalog/UKIDSS_OBSERVATION/DR11PLUS/UKIDSS_GPS/UKIDSS_GPS_${cloud}.csv"
                set header=13
            else if ( ${cloud} == PER ) then
                set ukidss_catalog="${YSO_table}/All_UKIDSS_Catalog/UKIDSS_OBSERVATION/DR11PLUS/Survey_Merging/UKIDSS_COMBINED_${cloud}.tbl"
                set header=0
            endif
            Add_Mag_JHK_UKIDSS_C2D_Combined.py catalog-${cloud}-HREL.tbl ${ukidss_catalog} ${header} \
                                           catalog-${cloud}-HREL-Add_Mag-Add_UKIDSS_JHK_2MASSBR.tbl 2MASSBR | tee -a ${logfile}
            echo "Adding artificial quality labels ..."
            Add_Mag_Qua_JHK_UKIDSS.py catalog-${cloud}-HREL-Add_Mag-Add_UKIDSS_JHK_2MASSBR.tbl default N A_fake | tee -a ${logfile}
            Add_Mag_Qua_JHK_UKIDSS.py catalog-${cloud}-HREL-Add_Mag-Add_UKIDSS_JHK_2MASSBR-Add_JHK_Qua.tbl default U A_fake | tee -a ${logfile}
            echo "Start setting neeed presets ..."
            SOP_Execution_Preset.py catalog-${cloud}-HREL-Add_Mag-Add_UKIDSS_JHK_2MASSBR-Add_JHK_Qua.tbl ${cloud} Self_made | tee -a ${logfile}
        else
            echo "Please check UKIDSS observation data ..."
        endif
    endif

    # Method to calculate galaxy probability
    echo "Calculating GP by diagonal boundary method ..."
    Calculate_GP_WI_6D_Diag_Bound_Array.py ${cloud}_saturate_correct_file.tbl ${cloud} mag \
    ${GP_dir} ${dim} ${cube} ${sigma} ${bond} ${refD} | tee -a ${logfile}
    set GP_out=${cloud}_${dim}D_diag_BD_GP_all_out_catalog.tbl

    # Classify YSO and compare to Hsieh's YSO candidates
    echo "Classifying and compare with Hsieh's YSOc ..."
    Classify_WI_6D_Diag_Galaxy_Prob.py ${GP_out} ${cloud} | tee -a ${logfile}
    Check_Coord.py ${cloud}_6D_YSO.tbl default ${cloud}_YSO default 7 False | tee -a ${logfile}
    Check_Coord.py ${cloud}_6D_Galaxy.tbl default ${cloud}_Galaxy default 7 False | tee -a ${logfile}
    Check_Coord.py ${cloud}_6D_GP_to_image_check.tbl default ${cloud}_6D_GP_IC default 7 False | tee -a ${logfile}
    Check_Coord.py ${cloud}_6D_GP_others.tbl default ${cloud}_6D_OTHERS default 7 False | tee -a ${logfile}
    Print_6D_GP_Confusion_Matrix.py ${cloud} | tee -a ${logfile}

    # Single cloud ends and change directory to next one
    echo "${cloud} completes ...\n"
    cd .. && pwd
end

# Merge all YSO candidates
echo "Merging all YSO candidates ..."
Merge_6D_Diag_BD_YSO_catalog.csh && cd All_YSO
Check_Coord.py all_GP_Diag_new_BYSO.tbl default all_GP_Diag_new_BYSO default 7 False | tee -a ${logfile}
Check_Coord.py all_GP_Diag_new_IYSO.tbl default all_GP_Diag_new_IYSO default 7 False | tee -a ${logfile}
Check_Coord.py all_GP_Diag_new_NIBYSO.tbl default all_GP_Diag_new_NIBYSO default 7 False | tee -a ${logfile}
cd .. && echo "Pipeline completed ...\n"
