from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components 
from bokeh.models.widgets import Button, RadioButtonGroup, Select, Slider
from bokeh.layouts import column, row, widgetbox, gridplot
from bokeh.models import CustomJS, ColumnDataSource, Range1d, LabelSet, Label

import numpy as np
from math import pi

import pickle

app = Flask(__name__)



# Load in some data
le_cat = ['Cancers and Other Neoplasms',
		 'Symptoms and General Pathology',
		 'Immune System Diseases',
		 'Urinary Tract, Sexual Organs, and Pregnancy Conditions',
		 'Digestive System Diseases',
		 'Skin and Connective Tissue Diseases',
		 'Respiratory Tract (Lung and Bronchial) Diseases',
		 'Nervous System Diseases',
		 'Nutritional and Metabolic Diseases',
		 'Blood and Lymph Conditions',
		 'Heart and Blood Diseases',
		 'Behaviors and Mental Disorders',
		 'Viral Diseases',
		 'Muscle, Bone, and Cartilage Diseases',
		 'Bacterial and Fungal Diseases',
		 'Wounds and Injuries',
		 'Gland and Hormone Related Diseases',
		 'Eye Diseases',
		 'Diseases and Abnormalities at or Before Birth',
		 'Substance Related Disorders',
		 'Mouth and Tooth Diseases',
		 'Parasitic Diseases',
		 'Ear, Nose, and Throat Diseases',
		 'Occupational Diseases']
 
le_phase = ['Early Phase 1',
	'Phase 1',
	'Phase 1/Phase 2',
	'Phase 2',
	'Phase 2/Phase 3',
	'Phase 3',
	'Phase 4']

arms_list = [ '-1',
    '0.0',
    '1.0',
    '2.0',
    '3.0',
    '4.0',
    '5.0',
    '6.0',
    '7.0',
    '8.0',
    '9.0',
    '10.0',
    '11.0',
    '12.0',
    '13.0',
    '14.0',
    '15.0',
    '16.0',
    '17.0',
    '18.0',
    '19.0',
    '20.0',
    '21.0',
    '22.0',
    '24.0',
    '27.0',
    '32.0']
    
le_ivn_type = ['Behavioral',
				'Biological',
				'Combination Product',
				'Device',
				'Diagnostic Test',
				'Dietary Supplement',
				'Drug',
				'Genetic',
				'Other',
				'Procedure',
				'Radiation']

mesh_cat_term_trial = dict({
		 'Cancers and Other Neoplasms' : 16380.0,
		 'Symptoms and General Pathology' : 15438.0,
		 'Immune System Diseases' : 9962.0,
		 'Urinary Tract, Sexual Organs, and Pregnancy Conditions' : 8160.0,
		 'Digestive System Diseases' : 6998.0,
		 'Skin and Connective Tissue Diseases': 6734.0,
		 'Respiratory Tract (Lung and Bronchial) Diseases' : 6678.0,
		 'Nervous System Diseases' : 4869.0,
		 'Nutritional and Metabolic Diseases' : 4478.0,
		 'Blood and Lymph Conditions' : 4350.0,
		 'Heart and Blood Diseases' : 4231.0,
		 'Behaviors and Mental Disorders' : 3065.0,
		 'Viral Diseases' : 2667.0,
		 'Muscle, Bone, and Cartilage Diseases' : 2660.0,
		 'Bacterial and Fungal Diseases' : 1688.0,
		 'Wounds and Injuries' : 1579.0,
		 'Gland and Hormone Related Diseases' : 1540.0,
		 'Eye Diseases': 1442.0,
		 'Diseases and Abnormalities at or Before Birth' : 776.0,
		 'Substance Related Disorders' : 776.0,
		 'Mouth and Tooth Diseases' : 570.0,
		 'Parasitic Diseases' : 274.0,
		 'Ear, Nose, and Throat Diseases' : 216.0,
		 'Occupational Diseases' : 0.0
		})
		
phase = dict({
	'Early Phase 1' : 774,
	'Phase 1' : 15510,
	'Phase 1/Phase 2' : 8480,
	'Phase 2' : 41579,
	'Phase 2/Phase 3' : 2582,
	'Phase 3' :18210,
	'Phase 4' :11320,
	})
	
arms =	dict({
	'0.0' : 10982.0,
	'1.0' : 38166.0,
	'2.0' : 45710.0,
	'3.0' : 10837.0,
	'4.0' : 6140.0,
	'5.0' : 1525.0,
	'6.0' : 1288.0,
	'7.0' : 354.0,
	'8.0' : 1454.0,
	'9.0' : 436.0,
	'10.0' : 156.0,
	'11.0' : 192.0,
	'12.0' : 40.0,
	'13.0' : 78.0,
	'14.0' : 42.0,
	'15.0' : 6.0,
	'16.0' : 20.0,
	'17.0' : 0.0,
	'18.0' :4.0,
	'19.0' : 0.0,
	'20.0' : 26.0,
	'21.0' : 0.0,
	'22.0' : 0.0,
	'24.0' : 0.0,
	'27.0' : 0.0,
	'32.0' : 0.0,
	})
	
ivn = dict({
	'Behavioral' : 1788.0,
	'Biological' : 7034.0,
	'Combination Product' : 0.0,
	'Device' : 5896.0,
	'Diagnostic Test' : 12.0,
	'Dietary Supplement' : 1518.0,
	'Drug' : 81401.0,
	'Genetic' : 564.0,
	'Other' : 7925.0,
	'Procedure' : 8808.0,
	'Radiation' : 2510.0,
	})
	


mesh_cat_data = sorted(mesh_cat_term_trial.items(), key=lambda x:x[1], reverse=True)		
mesh_cat_keys, mesh_cat_vals = zip(*mesh_cat_data)

phase_data = sorted(phase.items())
phase_keys, phase_vals = zip(*phase_data) 

arms_data = sorted([(float(k),v) for (k,v) in arms.items()])
arms_keys, arms_vals = zip(*arms_data)
arms_keys = [str(x) for x in arms_keys]

ivn_data = sorted(ivn.items(), key = lambda x:x[1], reverse=True)
ivn_keys, ivn_vals = zip(*ivn_data)

responsive=True

@app.route('/')
def fcn():
		
	return render_template('index.html', 
		disease_cats = mesh_cat_keys, 
		phase_ct = phase_keys,
		arms_ct = arms_keys,
		ivn_ct = ivn_keys)
	
@app.route('/index', methods=['GET','POST'])
def index():
	
	input_category=request.form['dcat']
	input_phase=request.form['phase']
	input_arms=request.form['arms']
	input_ivn=request.form['ivnt']

	######## Probability #########
	
	
	prob_key = '%s%s%s%s' %(le_cat.index(input_category), 
							le_phase.index(input_phase),
							arms_list.index(input_arms),
							le_ivn_type.index(input_ivn))
	
	
	prob_dict = pickle.load(open('prob_dict.p','rb'))
	
	#import pickle
	#tree_clf = pickle.load(open('tree_clf.dill', 'r'))
	
	#final_prob=tree_clf.predict_proba
	
	cat_key = '%s%s%s' %(le_phase.index(input_phase),
							arms_list.index(input_arms),
							le_ivn_type.index(input_ivn))
	probs_cat=list([str(format(prob_dict['%s%s' %('0',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('1',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('2',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('3',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('4',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('5',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('6',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('7',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('8',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('9',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('10',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('11',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('12',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('13',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('14',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('15',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('16',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('17',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('18',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('19',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('20',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('21',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('22',cat_key)], '.2f')),
					str(format(prob_dict['%s%s' %('23',cat_key)], '.2f'))])

	phase_key_one = '%s' %(le_cat.index(input_category))
	phase_key_two = '%s%s' %(arms_list.index(input_arms),
							le_ivn_type.index(input_ivn))
	probs_phase=list([str(format(prob_dict['%s%s%s' %(phase_key_one,'0',phase_key_two)], '.2f')),
					  str(format(prob_dict['%s%s%s' %(phase_key_one,'1',phase_key_two)], '.2f')),
					  str(format(prob_dict['%s%s%s' %(phase_key_one,'2',phase_key_two)], '.2f')),
					  str(format(prob_dict['%s%s%s' %(phase_key_one,'3',phase_key_two)], '.2f')),
					  str(format(prob_dict['%s%s%s' %(phase_key_one,'4',phase_key_two)], '.2f')),
					  str(format(prob_dict['%s%s%s' %(phase_key_one,'5',phase_key_two)], '.2f')),
					  str(format(prob_dict['%s%s%s' %(phase_key_one,'6',phase_key_two)], '.2f'))])
	
	arms_key_one = '%s%s' %(le_cat.index(input_category), 
							le_phase.index(input_phase))
	arms_key_two = '%s'	%(le_ivn_type.index(input_ivn))		  
	probs_arms=list([str(format(prob_dict['%s%s%s' %(arms_key_one,'0',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'1',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'2',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'3',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'4',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'5',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'6',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'7',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'8',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'9',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'10',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'11',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'12',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'13',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'14',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'15',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'16',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'17',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'18',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'19',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'20',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'21',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'22',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'23',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'24',arms_key_two)], '.2f')),
					str(format(prob_dict['%s%s%s' %(arms_key_one,'25',arms_key_two)], '.2f'))])
	
	ivn_key = '%s%s%s' %(le_cat.index(input_category), 
							le_phase.index(input_phase),
							arms_list.index(input_arms))
	probs_list=list([str(format(prob_dict['%s%s' %(ivn_key,'0')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'1')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'2')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'3')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'4')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'5')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'6')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'7')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'8')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'9')], '.2f')),
			         str(format(prob_dict['%s%s' %(ivn_key,'10')], '.2f'))])
	
	
	#	'0.WW', '0.88', '0.55', '0.45', '5', '6', '7', '8', '9','10', '11'] 

	
	
	mesh_cat_colors=list(['#efedf5'])*len(mesh_cat_keys)
	# format data
	labels,y=zip(*mesh_cat_data)
	
	header_text='Number of Incomplete Clinical Trials By Category'
	
	# make a bokeh figure
	#p = figure(x_range=mesh_cat_keys, plot_width=500, plot_height=455) # Good for half-computer screen
	p = figure(x_range=mesh_cat_keys, plot_width=500, plot_height=550) # Good for half-computer screen
	
	color_key=mesh_cat_keys.index(input_category)
	mesh_cat_colors[color_key]='#756bb1'
 
	second_cat = list([''])*len(mesh_cat_keys)
	second_cat[color_key]=probs_cat[color_key]
		
	source = ColumnDataSource(data=dict(p=probs_cat, y=mesh_cat_colors, z=second_cat))
	
	p.vbar(x=mesh_cat_keys, width=0.5, bottom=0, top=mesh_cat_vals, color='y', source=source)
	p.xaxis.major_label_orientation = pi/2
	
	p.text(18, 9500, text='z', text_color='#000000',
	         alpha=0.6667, text_font_size='36pt', text_baseline='middle',
	         text_align='center', source=source)
	
	callback = CustomJS(args=dict(source=source), code="""
		var data = source.data;
		var A = Math.round(dnum.value);
		
		probs = data['p'];
		colors = data['y'];
		second = data['z'];
		
		for (i = 0; i < colors.length; i++) {
		colors[i] = '#efedf5';
		}
		
		for (i = 0; i < second.length; i++) {
		second[i] = '';
		}				
		second[A] = probs[A];
		colors[A]='#756bb1';
		
		source.change.emit();
	""")

	mesh_cat_slider = Slider(start=0, end=23, value=color_key, step=1,
					title="Disease Category", callback=callback)
					
	callback.args["dnum"] = mesh_cat_slider
	
	############### Phase Figure ##############
	
	phase_colors=list(['#efedf5'])*len(phase_keys)
	
	header_phase='Number of Incomplete Clinical Trials By Phase'
	
	# make a bokeh figure
	p_phase = figure(x_range=phase_keys, plot_width=500, plot_height=300)
	
	color_key_phase=phase_keys.index(input_phase)
	phase_colors[color_key_phase]='#756bb1'
	
	second_phase = list([''])*len(phase_keys)
	second_phase[color_key_phase]=probs_phase[color_key_phase]
		
	source_phase = ColumnDataSource(data=dict(p=probs_phase, y=phase_colors, z=second_phase))
	
	p_phase.vbar(x=phase_keys, width=0.5, bottom=0, top=phase_vals, color='y', source=source_phase)
	p_phase.xaxis.major_label_orientation = pi/2
	
	p_phase.text(5.5, 30000, text='z', text_color='#000000',
	         alpha=0.6667, text_font_size='36pt', text_baseline='middle',
	         text_align='center', source=source_phase)
	
	callback_phase = CustomJS(args=dict(source=source_phase), code="""
		var data = source.data;
		var A = Math.round(dnum.value);
	
		probs = data['p'];
		colors = data['y'];
		second = data['z'];
		
		for (i = 0; i < colors.length; i++) {
		colors[i] = '#efedf5';
		}
		
		for (i = 0; i < second.length; i++) {
		second[i] = '';
		}				
		
		second[A] = probs[A];
		colors[A]='#756bb1'
		
		source.change.emit();
	""")

	phase_slider = Slider(start=0, end=6, value=color_key_phase, step=1,
					title="Phase", callback=callback_phase)
				
	callback_phase.args["dnum"] = phase_slider
	
	############# Arms Figure ################
	
	arms_colors=list(['#efedf5'])*len(arms_keys)
	
	header_arms='Number of Incomplete Clinical Trials By Number of Arms'
	
	# make a bokeh figure
	p_arms = figure(x_range=arms_keys, plot_width=500, plot_height=300)
	
	color_key_arms=arms_keys.index(input_arms)
	arms_colors[color_key_arms]='#756bb1'

	second_arms = list([''])*len(arms_keys)
	second_arms[color_key_arms]=probs_arms[color_key_arms]
	
	source_arms = ColumnDataSource(data=dict(p=probs_arms, y=arms_colors, z=second_arms))
	
	p_arms.vbar(x=arms_keys, width=0.5, bottom=0, top=arms_vals, color='y', source=source_arms)
	p_arms.xaxis.major_label_orientation = pi/2
	
	p_arms.text(18, 30000, text='z', text_color='#000000',
	         alpha=0.6667, text_font_size='36pt', text_baseline='middle',
	         text_align='center', source=source_arms)
	
	callback_arms = CustomJS(args=dict(source=source_arms), code="""
		var data = source.data;
		var A = Math.round(dnum.value);
		
		probs = data['p'];
		colors = data['y'];
		second = data['z'];
		
		for (i = 0; i < colors.length; i++) {
		colors[i] = '#efedf5';
		}
		
		for (i = 0; i < second.length; i++) {
		second[i] = '';
		}
		
		second[A] = probs[A];
		colors[A] = '#756bb1'
		
		source.change.emit();
	""")

	arms_slider = Slider(start=0, end=len(arms_keys)-1, value=color_key_arms, step=1,
					title="Arms", callback=callback_arms)
				
	callback_arms.args["dnum"] = arms_slider
	
	############ Intervention Figure ##################
	ivn_colors=list(['#efedf5'])*len(ivn_keys)
	
	header_ivn='Number of Incomplete Clinical Trials By Intervention'
	
	# make a bokeh figure
	p_ivn = figure(x_range=ivn_keys, plot_width=500, plot_height=300)
	
	color_key_ivn=ivn_keys.index(input_ivn)
	ivn_colors[color_key_ivn]='#756bb1'
	
	second_labels = list([''])*len(ivn_keys)
	second_labels[color_key_ivn]=probs_list[color_key_ivn]
	
	source_ivn = ColumnDataSource(data=dict(p=probs_list, y=ivn_colors, z=second_labels))
	
	p_ivn.vbar(x=ivn_keys, width=0.5, bottom=0, top=ivn_vals, color='y', source=source_ivn)
	p_ivn.xaxis.major_label_orientation = pi/2

	p_ivn.text(8, 60000, text='z', text_color='#000000',
	         alpha=0.6667, text_font_size='36pt', text_baseline='middle',
	         text_align='center', source=source_ivn)
	
	# p1.text(0, 0, text='color', text_color='text_color',
	#         alpha=0.6667, text_font_size='36pt', text_baseline='middle',
	#         text_align='center', source=source)
	
	# 	cit_ivn = Label(x=100, y=150, x_units='screen', y_units='screen',
	# 	            text=source_ivn, render_mode='css', text_font_size='100pt',
	# 	  	 		 border_line_alpha=1.0,
	#                  background_fill_color='white', background_fill_alpha=1.0,
	#                  )
	# 	p_ivn.add_layout(cit_ivn)
		
	callback_ivn = CustomJS(args=dict(source=source_ivn), code="""
		var data = source.data;
		var A = Math.round(dnum.value);
		
		probs = data['p'];
		colors = data['y'];
		second = data['z'];
		
		for (i = 0; i < colors.length; i++) {
		colors[i] = '#efedf5';
		}

		for (i = 0; i < second.length; i++) {
		second[i] = '';
		}				
		
		second[A] = probs[A];					
		colors[A] = '#756bb1';
		
		source.change.emit();
	""")

	ivn_slider = Slider(start=0, end=len(ivn_keys)-1, value=color_key_ivn, step=1,
					title="Intervention", callback=callback_ivn)
				
	callback_ivn.args["dnum"] = ivn_slider
	
	######## components ##############		
	script, div = components(column(p,row(widgetbox(mesh_cat_slider)), responsive=responsive))
	script_phase, div_phase = components(column(p_phase, row(widgetbox(phase_slider)), responsive=responsive))
	script_arms, div_arms = components(column(p_arms, row(widgetbox(arms_slider)), responsive=responsive))
	script_ivn, div_ivn = components(column(p_ivn, row(widgetbox(ivn_slider)), responsive=responsive))
	
	return render_template('graph2.html', script=script, div=div, h=header_text,
		script_phase=script_phase, div_phase=div_phase, hp=header_phase,
		script_arms=script_arms, div_arms=div_arms, ha=header_arms,
		script_ivn=script_ivn, div_ivn=div_ivn, hi=header_ivn
		)
	 
	#return render_template('graph2.html',
	#	script_phase=script_phase, div_phase=div_phase, hp=header_phase
	#	)
	
	 
	# 							s=script2, div2=div2, h2=header2)

	# 
	# 	bot_ten=dict({
	# 			'Hellenic Oncology Research Group' : 0.580153,
	# 			'Northside Hospital, Inc.' : 0.551320,
	# 			'Vanderbilt-Ingram Cancer Center' : 0.507132,
	# 			'University of Medicine and Dentistry of New Jersey' : 0.467797,
	# 			'H. Lee Moffitt Cancer Center and Research Institute' : 0.435455,
	# 			'Masonic Cancer Center, University of Minnesota' : 0.423792,
	# 			'OHSU Knight Cancer Institute' : 0.354819,
	# 			'Therapeutic Advances in Childhood Leukemia Consortium' : 0.314220,
	# 			'King\'s College Hospital NHS Trust' : 0.250000,
	# 			'Fairview University Medical Center' : 0.111842,
	# 			})
	# 		
	# 	labels2,y2=zip(*bot_ten.items())
	# 	
	# 	# make a bokeh figure
	# 	p2 = figure(x_range=labels2, plot_height=600) #plot_width=400, plot_height=400)
	# 	# add a circle renderer with a size, color, and alpha
	# 	#p.circle(dates, prices, size=20, color="navy", alpha=0.5)
	# 	p2.vbar(x=labels2,width=0.5, bottom=0, top=y2)
	# 	p2.xaxis.major_label_orientation = pi/2
	# 	
	# 	script2, div2 = components(p2)
	# 	header2='Rate of Completion by Sponsor'
	# 
	# 	#return render_template('graph.html', script=script, div=div, h=header_text)	
	# 	return render_template('graph2.html', script=script, div=div, h=header_text, 
	# 							s=script2, div2=div2, h2=header2)

if __name__ == '__main__':
	app.run() #port=33507, debug=True)
