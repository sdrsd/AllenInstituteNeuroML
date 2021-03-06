'''

    Still under developemnt!!

    Subject to change without notice!!

'''

from pyneuroml.tune.NeuroMLTuner import run_optimisation, run_2stage_optimization

from pyneuroml.tune.NeuroMLController import NeuroMLController

import neuroml

import sys
from collections import OrderedDict

import json
import os


import random

import pprint
pp = pprint.PrettyPrinter(indent=4)


from pyneuroml import pynml

sys.path.append("../data")
import data_helper as DH
sys.path.append("../data/bulk_analysis")
import bulk_data_helper as BDH

#####    Pospischil et al 2008
              
parameters_hh = ['cell:RS/channelDensity:LeakConductance_all/mS_per_cm2',
              'cell:RS/erev_id:LeakConductance_all/mV',
              'cell:RS/specificCapacitance:all/uF_per_cm2',
              'cell:RS/channelDensity:Na_all/mS_per_cm2',
              'cell:RS/channelDensity:Kd_all/mS_per_cm2',
              'cell:RS/channelDensity:IM_all/mS_per_cm2',
              'cell:RS/erev_id:Na_all/mV',
              'cell:RS/erev_id:Kd_all/mV',
              'cell:RS/erev_id:IM_all/mV']


max_constraints_hh = [0.2,   -60,  4,  80, 30, 5,    60, -70, -70]
min_constraints_hh = [0.01, -100, 0.2, 10, 1, 1e-3, 50, -90, -90]


#  typical (tuned) spiking cell
example_vars_hh = {'cell:RS/channelDensity:IM_all/mS_per_cm2': 0.18764779330203835,
                'cell:RS/channelDensity:Kd_all/mS_per_cm2': 16.95202053476659,
                'cell:RS/channelDensity:LeakConductance_all/mS_per_cm2': 0.09988609723098822,
                'cell:RS/channelDensity:Na_all/mS_per_cm2': 30.229674358155705,
                'cell:RS/erev_id:IM_all/mV': -81.1091911447433,
                'cell:RS/erev_id:Kd_all/mV': -70,
                'cell:RS/erev_id:LeakConductance_all/mV': -77.62455951121044,
                'cell:RS/erev_id:Na_all/mV': 55.053832510995626,
                'cell:RS/specificCapacitance:all/uF_per_cm2': 1.9607901262899832}

#####    Izhikevich 2007 cell model

parameters_iz = ['izhikevich2007Cell:RS/a/per_ms',
                 'izhikevich2007Cell:RS/b/nS',
                 'izhikevich2007Cell:RS/c/mV',
                 'izhikevich2007Cell:RS/d/pA',
                 'izhikevich2007Cell:RS/C/pF',
                 'izhikevich2007Cell:RS/vr/mV',
                 'izhikevich2007Cell:RS/vt/mV',
                 'izhikevich2007Cell:RS/vpeak/mV',
                 'izhikevich2007Cell:RS/k/nS_per_mV']

# Example parameter ranges for above
#                     a,     b,  c,  d,   C,    vr,  vt, vpeak, k
min_constraints_iz = [0.01, -5, -65, 10,  30,  -90, -60, 0,    0.1]
max_constraints_iz = [0.2,  20, -10, 400, 300, -70,  50, 70,   1]

#  typical (tuned) spiking cell
example_vars_iz = {'izhikevich2007Cell:RS/C/pF': 121.89939137782264,
                    'izhikevich2007Cell:RS/a/per_ms': 0.08048276778661327,
                    'izhikevich2007Cell:RS/b/nS': 0.42252877652260556,
                    'izhikevich2007Cell:RS/c/mV': -45.823508919072445,
                    'izhikevich2007Cell:RS/d/pA': 214.2736731101308,
                    'izhikevich2007Cell:RS/k/nS_per_mV': 0.22246514332222897,
                    'izhikevich2007Cell:RS/vpeak/mV': 32.332261968942376,
                    'izhikevich2007Cell:RS/vr/mV': -78.1568627395237,
                    'izhikevich2007Cell:RS/vt/mV': -21.563700799975003}
                   
                   


####  Test target data

ref = 'Pop0/0/RS/v:'
average_maximum = ref+'average_maximum'
average_minimum = ref+'average_minimum'
mean_spike_frequency = ref+'mean_spike_frequency'
#first_spike_time = ref+'first_spike_time'
average_last_1percent = ref+'average_last_1percent'

weights = {average_maximum: 1,
           average_minimum: 1,
           mean_spike_frequency: 5,
           average_last_1percent: 1}

target_data = {average_maximum: 33.320915,
               average_minimum: -44.285,
               mean_spike_frequency: 26.6826,
               average_last_1percent: -80}



####     Target data


def get_2stage_target_values(dataset_id):

    
    if os.path.isdir("../data/%s_analysis.json"%dataset_id):
        
        target_sweep_numbers = DH.DATASET_TARGET_SWEEPS
        sweep_numbers = target_sweep_numbers[dataset_id]
        
        with open("../data/%s_analysis.json"%dataset_id, "r") as json_file:
            metadata = json.load(json_file)
    else:
        
        target_sweep_numbers = BDH.DATASET_TARGET_SWEEPS
        sweep_numbers = target_sweep_numbers[dataset_id]
        
        with open("../data/bulk_analysis/%s_analysis.json"%dataset_id, "r") as json_file:
            metadata = json.load(json_file)

    ref0 = 'Pop0/0/RS/v:'
    ref1 = 'Pop0/1/RS/v:'
    ref2 = 'Pop0/2/RS/v:'
    ref3 = 'Pop0/3/RS/v:'
    ref5 = 'Pop0/5/RS/v:'
    ref6 = 'Pop0/6/RS/v:'

    steady_average = 'average_1000_1200'
    steady0 = ref0+steady_average
    average_last_1percent0 = ref0+'average_last_1percent'
    ref0_280 = ref0+'value_280'
    steady1 = ref1+steady_average
    steady2 = ref2+steady_average
    steady3 = ref3+steady_average


    weights_1 = {steady0: 10,
                 average_last_1percent0: 1,
                 ref0_280: 1,
                 steady1: 1,
                 steady2: 1,
                 steady3: 1}

    sw0 = "%s"%sweep_numbers[0]
    sw1 = "%s"%sweep_numbers[1]
    sw2 = "%s"%sweep_numbers[2]
    sw3 = "%s"%sweep_numbers[3]
    sw4 = "%s"%sweep_numbers[4]
    sw5 = "%s"%sweep_numbers[5]
    sw6 = "%s"%sweep_numbers[6]

    target_data_1 = {steady0:                metadata['sweeps'][sw0]["pyelectro_iclamp_analysis"][sw0+":"+steady_average],
                     average_last_1percent0: metadata['sweeps'][sw0]["pyelectro_iclamp_analysis"][sw0+":average_last_1percent"],
                     ref0_280:               metadata['sweeps'][sw0]["pyelectro_iclamp_analysis"][sw0+":value_280"],
                     steady1:                metadata['sweeps'][sw1]["pyelectro_iclamp_analysis"][sw1+":"+steady_average],
                     steady2:                metadata['sweeps'][sw2]["pyelectro_iclamp_analysis"][sw2+":"+steady_average],
                     steady3:                metadata['sweeps'][sw3]["pyelectro_iclamp_analysis"][sw3+":"+steady_average]}

    average_maximum6 = ref6+'average_maximum'
    average_minimum6 = ref6+'average_minimum'
    mean_spike_frequency6 = ref6+'mean_spike_frequency'
    mean_spike_frequency5 = ref5+'mean_spike_frequency'

    weights_2 = {average_maximum6: 1,
               average_minimum6: 1,
               mean_spike_frequency6: 1,
               mean_spike_frequency5: 1}

    for w in weights_1.keys():
        weights_2[w] = weights_1[w]*0.5

    target_data_2 = {average_maximum6:      metadata['sweeps'][sw6]["pyelectro_iclamp_analysis"][sw6+":average_maximum"],
                     average_minimum6:      metadata['sweeps'][sw6]["pyelectro_iclamp_analysis"][sw6+":average_minimum"],
                     mean_spike_frequency6: metadata['sweeps'][sw6]["pyelectro_iclamp_analysis"][sw6+":mean_spike_frequency"],
                     mean_spike_frequency5: metadata['sweeps'][sw5]["pyelectro_iclamp_analysis"][sw5+":mean_spike_frequency"]} 

    for td in target_data_1.keys():
        target_data_2[td] = target_data_1[td]

    return sweep_numbers, weights_1, target_data_1, weights_2, target_data_2
    
    
def run_one_optimisation(ref,
                     seed,
                     population_size,
                     max_evaluations,
                     num_selected,
                     num_offspring,
                     mutation_rate,
                     num_elites,
                     simulator,
                     nogui,
                     parameters,
                     max_constraints,
                     min_constraints,
                     neuroml_file =     'prototypes/RS/AllenTest.net.nml',
                     target =           'network_RS',
                     weights =          weights,
                     target_data =      target_data,
                     dt =               0.025,
                     num_parallel_evaluations = 1):

    ref = '%s__s%s_p%s_m%s_s%s_o%s_m%s_e%s'%(ref,
                     seed,
                     population_size,
                     max_evaluations,
                     num_selected,
                     num_offspring,
                     mutation_rate,
                     num_elites)           

    return run_optimisation(prefix =           ref, 
                     neuroml_file =     neuroml_file,
                     target =           target,
                     parameters =       parameters,
                     max_constraints =  max_constraints,
                     min_constraints =  min_constraints,
                     weights =          weights,
                     target_data =      target_data,
                     sim_time =         1500,
                     dt =               dt,
                     seed =             seed,
                     population_size =  population_size,
                     max_evaluations =  max_evaluations,
                     num_selected =     num_selected,
                     num_offspring =    num_offspring,
                     mutation_rate =    mutation_rate,
                     num_elites =       num_elites,
                     simulator =        simulator,
                     nogui =            nogui,
                     num_parallel_evaluations = num_parallel_evaluations)



def scale(scale, number, min_=1, max_=sys.maxint):
    num = max(min_, int(scale*number))
    return min(max_, num)





def compare(sim_data_file, show_plot_already=True, dataset=471141261):
    dat_file_name = '../data/%s.dat'%dataset
    
    x = []
    y = []
    colors = []
    linestyles = []

    data, indeces = pynml.reload_standard_dat_file(dat_file_name)

    for ii in indeces:
        x.append(data['t'])
        y.append(data[ii])
        colors.append('lightgrey')
        linestyles.append('-')

    data, indeces = pynml.reload_standard_dat_file(sim_data_file)

    r = lambda: random.randint(0,255)

    for ii in indeces:
        x.append(data['t'])
        y.append(data[ii])
        c = '#%02X%02X%02X' % (r(),r(),r())
        colors.append(c)
        linestyles.append('-')

    pynml.generate_plot(x,
                        y, 
                        "Comparing tuned cell (in %s) to data: %s"%(sim_data_file, dataset), 
                        xaxis = 'Input current (nA)', 
                        yaxis = 'Membrane potential (mV)', 
                        colors = colors, 
                        linestyles = linestyles, 
                        show_plot_already=show_plot_already)


def run_2_stage_hh(dataset, simulator  = 'jNeuroML_NEURON', scale1=1, scale2=1,seed = 1234678, nogui=False,mutation_rate = 0.9):
    
        print("Running 2 stage hh optimisation")
        
        type = 'HH'
        ref = 'network_%s_%s'%(dataset, type)

        max_constraints_1 = [1,   -50,  5,   0, 0, 0, 55, -80, -80]
        min_constraints_1 = [0.001, -100, 0.2, 0, 0, 0, 55, -80, -80]

        # For a quick test...
        # max_constraints_1 = [0.1,   -77.9, 0.51,   0, 0, 0, 55, -80, -80]
        # min_constraints_1 = [0.09,  -77.8, 0.52,   0, 0, 0, 55, -80, -80]

        max_constraints_2 = ['x',   'x',   'x',    100,  35,   5,    60, -70,  -70]
        min_constraints_2 = ['x',   'x',   'x',    10,   1,    1e-6, 50, -100, -100]

        sweep_numbers, weights_1, target_data_1, weights_2, target_data_2 = get_2stage_target_values(dataset)


        r1, r2 = run_2stage_optimization('Allen2stage',
                                neuroml_file = 'prototypes/RS/%s.net.nml'%ref,
                                target =        ref,
                                parameters = parameters_hh,
                                max_constraints_1 = max_constraints_1,
                                max_constraints_2 = max_constraints_2,
                                min_constraints_1 = min_constraints_1,
                                min_constraints_2 = min_constraints_2,
                                delta_constraints = 0.01,
                                weights_1 = weights_1,
                                weights_2 = weights_2,
                                target_data_1 = target_data_1,
                                target_data_2 = target_data_2,
                                sim_time = 1500,
                                dt = 0.01,
                                population_size_1 = scale(scale1,100,10),
                                population_size_2 = scale(scale2,100,10),
                                max_evaluations_1 = scale(scale1,500,20),
                                max_evaluations_2 = scale(scale2,500,10),
                                num_selected_1 = scale(scale1,30,5),
                                num_selected_2 = scale(scale2,30,5),
                                num_offspring_1 = scale(scale1,30,5),
                                num_offspring_2 = scale(scale2,30,5),
                                mutation_rate = mutation_rate,
                                num_elites = scale(scale2,5,2),
                                simulator = simulator,
                                nogui = nogui,
                                show_plot_already = False,
                                seed = seed,
                                known_target_values = {},
                                dry_run = False,
                                num_parallel_evaluations = 12,
                                extra_report_info = {'dataset':dataset,"Prototype":"HH"})
        
        if not nogui:
            compare('%s/%s.Pop0.v.dat'%(r1['run_directory'], r1['reference']), show_plot_already=False,    dataset=dataset)
            compare('%s/%s.Pop0.v.dat'%(r2['run_directory'], r2['reference']), show_plot_already=not nogui,dataset=dataset)
        
        
        final_network = '%s/%s.net.nml'%(r2['run_directory'], ref)
        
        nml_doc = pynml.read_neuroml2_file(final_network)
        
        cell = nml_doc.cells[0]
        
        print("Extracted cell: %s from tuned model"%cell.id)
        
        new_id = '%s_%s'%(type, dataset)
        new_cell_doc = neuroml.NeuroMLDocument(id=new_id)
        cell.id = new_id
        
        cell.notes = "Cell model tuned to Allen Institute Cell Types Database, dataset: "+ \
                     "%s\n\nTuning procedure metadata:\n\n%s\n"%(dataset, pp.pformat(r2))
        
        new_cell_doc.cells.append(cell)
        new_cell_file = 'tuned_cells/%s.cell.nml'%new_id
        
        channel_files = ['IM.channel.nml', 'Kd.channel.nml', 'Leak.channel.nml', 'Na.channel.nml']
        for ch in channel_files:
            new_cell_doc.includes.append(neuroml.IncludeType(ch))
            
        pynml.write_neuroml2_file(new_cell_doc, new_cell_file)



def run_2_stage_izh(dataset, simulator  = 'jNeuroML_NEURON', scale1=1, scale2=1,seed = 1234678, nogui=False):
    
    type = 'Izh'
    ref = 'network_%s_%s'%(dataset, type)

    #                     a,   b,  c,  d,   C,    vr,  vt, vpeak, k
    min_constraints_1 = [0.1, 1, -50, 300,  30,  -90, -30, 30,   0.01]
    max_constraints_1 = [0.1, 1, -50, 300, 300,  -70, -30, 30,   1]


    #                     a,     b,  c,  d,   C,    vr,  vt, vpeak, k
    min_constraints_2 = [0.01, -5, -65, 10,  'x',  'x', -60, 0,   'x']
    max_constraints_2 = [0.2,  20, -10, 400, 'x',  'x',  50, 70,  'x']

    sweep_numbers, weights_1, target_data_1, weights_2, target_data_2 = get_2stage_target_values(dataset)

    mutation_rate = 0.1,
    num_elites = scale(scale2,8,2,10),


    r1, r2 = run_2stage_optimization('AllenIzh2stage',
                            neuroml_file = 'prototypes/RS/%s.net.nml'%ref,
                            target = ref,
                            parameters = parameters_iz,
                            max_constraints_1 = max_constraints_1,
                            max_constraints_2 = max_constraints_2,
                            min_constraints_1 = min_constraints_1,
                            min_constraints_2 = min_constraints_2,
                            delta_constraints = 0.01,
                            weights_1 = weights_1,
                            weights_2 = weights_2,
                            target_data_1 = target_data_1,
                            target_data_2 = target_data_2,
                            sim_time = 1500,
                            dt = 0.05,
                            population_size_1 = scale(scale1,100,10),
                            population_size_2 = scale(scale2,100,10),
                            max_evaluations_1 = scale(scale1,800,20),
                            max_evaluations_2 = scale(scale2,800,10),
                            num_selected_1 = scale(scale1,30,5),
                            num_selected_2 = scale(scale2,30,5),
                            num_offspring_1 = scale(scale1,20,5),
                            num_offspring_2 = scale(scale2,20,5),
                            mutation_rate = mutation_rate,
                            num_elites = num_elites,
                            simulator = simulator,
                            nogui = nogui,
                            show_plot_already = True,
                            seed = seed,
                            known_target_values = {},
                            dry_run = False,
                            num_parallel_evaluations = 12,
                            extra_report_info = {'dataset':dataset,"Prototype":"Izhikevich"})


    if not nogui:       
        compare('%s/%s.Pop0.v.dat'%(r1['run_directory'], r1['reference']), show_plot_already=False,     dataset=dataset)
        compare('%s/%s.Pop0.v.dat'%(r2['run_directory'], r2['reference']), show_plot_already=not nogui, dataset=dataset)

    final_network = '%s/%s.net.nml'%(r2['run_directory'], ref)

    nml_doc = pynml.read_neuroml2_file(final_network)

    cell = nml_doc.izhikevich2007_cells[0]

    print("Extracted cell: %s from tuned model"%cell.id)

    new_id = '%s_%s'%(type, dataset)
    new_cell_doc = neuroml.NeuroMLDocument(id=new_id)
    cell.id = new_id

    cell.notes = "Cell model tuned to Allen Institute Cell Types Database, dataset: "+ \
                 "%s\n\nTuning procedure metadata:\n\n%s\n"%(dataset, pp.pformat(r2))

    new_cell_doc.izhikevich2007_cells.append(cell)
    new_cell_file = 'tuned_cells/%s.cell.nml'%new_id

    pynml.write_neuroml2_file(new_cell_doc, new_cell_file)



if __name__ == '__main__':

    nogui = '-nogui' in sys.argv

    if '-compare' in sys.argv:

        compare('NT_AllenIzh__s12345_p200_m600_s80_o60_m0.1_e2_Mon_Nov_30_12.30.28_2015/AllenIzh__s12345_p200_m600_s80_o60_m0.1_e2.Pop0.v.dat')


    ####  Run simulation with one HH cell
    elif '-one' in sys.argv:   

        simulator  = 'jNeuroML_NEURON'
        #simulator  = 'jNeuroML'

        cont = NeuroMLController('AllenTest', 
                                 'prototypes/RS/AllenTest.net.nml',
                                 'network_RS',
                                 1500, 
                                 0.01, 
                                 simulator)

        sim_vars = OrderedDict(example_vars_hh)
        
        t, v = cont.run_individual(sim_vars, show=(not nogui))


    ####  Run simulation with multiple HH cells
    elif '-mone' in sys.argv:

        simulator  = 'jNeuroML_NEURON'
        #simulator  = 'jNeuroML'
        dataset = 471141261

        ref = 'network_%s_HH'%(dataset)
        cont = NeuroMLController('AllenTest', 
                                 'prototypes/RS/%s.net.nml'%ref,
                                 ref,
                                 1500, 
                                 0.01, 
                                 simulator)

        sim_vars = OrderedDict(example_vars_hh)
        
        t, v = cont.run_individual(sim_vars, show=(not nogui))


    ####  Run simulation with one Izhikevich cell
    elif '-izhone' in sys.argv:

        simulator  = 'jNeuroML'
        simulator  = 'jNeuroML_NEURON'

        cont = NeuroMLController('AllenIzhTest', 
                                 'prototypes/RS/AllenIzh.net.nml',
                                 'network_RS',
                                 1500, 
                                 0.05, 
                                 simulator)


        sim_vars = OrderedDict(example_vars_iz)

        t, v = cont.run_individual(sim_vars, show=(not nogui))


    ####  Run simulation with multiple Izhikevich cells
    elif '-izhmone' in sys.argv:

        simulator  = 'jNeuroML'
        simulator  = 'jNeuroML_NEURON'
        
        dataset = 471141261
        #dataset = 464198958
        
        ref = 'network_%s_Izh'%(dataset)
        cont = NeuroMLController('AllenIzhMulti', 
                                 'prototypes/RS/%s.net.nml'%ref,
                                 ref,
                                 1500, 
                                 0.05, 
                                 simulator)

        sim_vars = OrderedDict(example_vars_iz)

        t, v = cont.run_individual(sim_vars, show=(not nogui))



    ####  Run a 'quick' optimisation for Izhikevich cell model
    elif '-izhquick' in sys.argv:

        simulator  = 'jNeuroML_NEURON'

        scale1 = 0.1
        
        dataset = 479704527
        ref = 'network_%s_Izh'%(dataset)

        report = run_one_optimisation('AllenIzh',
                            12345,
                            parameters =       parameters_iz,
                            max_constraints =  max_constraints_iz,
                            min_constraints =  min_constraints_iz,
                            population_size =  scale(scale1,100),
                            max_evaluations =  scale(scale1,500),
                            num_selected =     scale(scale1,30),
                            num_offspring =    scale(scale1,30),
                            mutation_rate =    0.1,
                            num_elites =       2,
                            simulator =        simulator,
                            nogui =            nogui,
                            dt =               0.05,
                            neuroml_file =     'prototypes/RS/%s.net.nml'%ref,
                            target =           ref)

        compare('%s/%s.Pop0.v.dat'%(report['run_directory'], report['reference']), dataset=dataset)


    ####  Testing scaling...
    elif '-test' in sys.argv:

        simulator  = 'jNeuroML'

        scale1 = .2
        
        dataset = 464198958
        ref = 'network_%s_Izh'%(dataset)

        report = run_one_optimisation('AllenIzh',
                            123,
                            parameters =       parameters_iz,
                            max_constraints =  max_constraints_iz,
                            min_constraints =  min_constraints_iz,
                            population_size =  scale(scale1,100),
                            max_evaluations =  scale(scale1,500),
                            num_selected =     scale(scale1,30),
                            num_offspring =    scale(scale1,30),
                            mutation_rate =    0.1,
                            num_elites =       2,
                            simulator =        simulator,
                            nogui =            nogui,
                            dt =               0.05,
                            neuroml_file =     'prototypes/RS/%s.net.nml'%ref,
                            target =           ref,
                            num_parallel_evaluations = 10)

        compare('%s/%s.Pop0.v.dat'%(report['run_directory'], report['reference']), dataset=dataset)


    ####  Run a 2 stage optimisation for Izhikevich cell model

    elif '-izh2stage' in sys.argv:

        print("Running 2 stage optimisation")
        simulator  = 'jNeuroML_NEURON'
        dataset = 471141261
        dataset = 325941643
        dataset = 479704527
        dataset = 464198958
        dataset = 485058595
        dataset = 480169178
        dataset = 480351780
        dataset = 468120757
        dataset = 480353286
        
        scale1 = .5
        scale2 = .5
        seed = 12345
        
        
        if len(sys.argv)>2:
            print("Parsing args: %s"%sys.argv)
            dataset = int(sys.argv[3])
            simulator = sys.argv[4]
            scale1 = float(sys.argv[5])
            scale2 = float(sys.argv[6])
            seed = float(sys.argv[7])
        
        run_2_stage_izh(dataset, simulator, scale1, scale2,seed, nogui=nogui)
        


    ####  Run a 'quick' optimisation for HH cell model
    elif '-quick' in sys.argv:

        simulator  = 'jNeuroML_NEURON'
        
        dataset = 471141261
        ref = 'network_%s_HH'%(dataset)
        
        report = run_one_optimisation('AllenTestQ',
                            1234,
                            parameters =       parameters_hh,
                            max_constraints =  max_constraints_hh,
                            min_constraints =  min_constraints_hh,
                            population_size =  10,
                            max_evaluations =  30,
                            num_selected =     5,
                            num_offspring =    5,
                            mutation_rate =    0.9,
                            num_elites =       1,
                            neuroml_file =     'prototypes/RS/%s.net.nml'%ref,
                            target =           ref,
                            simulator =        simulator,
                            dt =               0.025,
                            nogui =            nogui)

        compare('%s/%s.Pop0.v.dat'%(report['run_directory'], report['reference']))


    ####  Run a 2 stage optimisation for HH cell model
    elif '-2stage' in sys.argv:

        print("Running 2 stage hh optimisation")
        simulator  = 'jNeuroML_NEURON'
        dataset = 471141261
        dataset = 479704527
        dataset = 325941643
        dataset = 464198958
        dataset = 485058595
        dataset = 486111903
        
        scale1 = 1
        scale2 = 1.5
        seed = 12345
        if len(sys.argv)>2:
            print("Parsing args: %s"%sys.argv)
            dataset = int(sys.argv[3])
            simulator = sys.argv[4]
            scale1 = float(sys.argv[5])
            scale2 = float(sys.argv[6])
            seed = float(sys.argv[7])
        
        run_2_stage_hh(dataset, simulator, scale1, scale2,seed, nogui=nogui,mutation_rate = 0.9)
        
    elif '-all' in sys.argv:
        

        simulator  = 'jNeuroML_NEURON'
        
        scale1 = 2
        scale2 = 4
        seed = 123456
        
        sys.path.append("../data")
        import data_helper as DH

        dataset_ids = DH.CURRENT_DATASETS
        #dataset_ids = [485058595]
        
        f = open('tuneAll.sh','w')

        for dataset_id in dataset_ids:
            f.write('python tuneAllen.py -2stage -nogui %s %s %s %s %s\n'%(dataset_id,simulator, scale1, scale2,seed))
            ###f.write('python tuneAllen.py -izh2stage -nogui %s %s %s %s %s\n'%(dataset_id,simulator, scale1, scale2,seed))
            #run_2_stage_hh(dataset_id, simulator, scale1, scale2, seed, nogui=True)
            #run_2_stage_izh(dataset_id, simulator, scale1, scale2, seed, nogui=True)
            f.write('swapoff -a\n')
            f.write('swapon -a\n\n')
        f.close()
        
    elif '-bulk' in sys.argv:
        

        simulator  = 'jNeuroML_NEURON'
        
        scale1 = 2
        scale2 = 2
        seed = 1234567
        
        sys.path.append("../data")
        import data_helper as DH
        sys.path.append("../data/bulk_analysis")
        import bulk_data_helper as BDH

        dataset_ids = BDH.CURRENT_DATASETS
        #dataset_ids = [485058595]
        
        f = open('tuneBulk.sh','w')

        for dataset_id in dataset_ids:
            if not dataset_id in DH.CURRENT_DATASETS:
                f.write('python tuneAllen.py -2stage -nogui %s %s %s %s %s\n'%(dataset_id,simulator, scale1, scale2,seed))
                ###f.write('python tuneAllen.py -izh2stage -nogui %s %s %s %s %s\n'%(dataset_id,simulator, scale1, scale2,seed))
                #run_2_stage_hh(dataset_id, simulator, scale1, scale2, seed, nogui=True)
                #run_2_stage_izh(dataset_id, simulator, scale1, scale2, seed, nogui=True)
                f.write('swapoff -a\n')
                f.write('swapon -a\n\n')
        f.close()

    else:

        print("Options to try:\n\n   (Izhikevich cell model)")
        print("     python tuneAllen.py -izhone     (run one Izhikevich cell with typical values)")
        print("     python tuneAllen.py -izhmone    (run multiple Izhikevich cells with different current inputs)")
        print("     python tuneAllen.py -izhquick   (quick optimisation example using Izhikevich cell)")
        print("     python tuneAllen.py -izh2stage  (2 stage optimisation example using Izhikevich cell)")
        print("\n   (HH cell model, based on Pospischil et al 2008)")
        print("     python tuneAllen.py -one    (run one HH cell with typical values)")
        print("     python tuneAllen.py -mone   (run multiple HH cells with different current inputs)")
        print("     python tuneAllen.py -quick  (quick optimisation example using HH cell)")
        print("     python tuneAllen.py -2stage  (2 stage optimisation example using HH cell)\n")



