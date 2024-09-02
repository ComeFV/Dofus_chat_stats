import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio
import numpy as np
import re

pio.templates.default = "plotly"

class Entity:
    def __init__(self, name):
        self.name = name 
        self.skill_summary = pd.DataFrame(columns=["skill", "damage", "heal received", "shield received", "target"])

    def add_action(self, skill, effect, value, target):
        new_row = {"skill":skill, effect:value, "target":target}
        new_row_df = pd.DataFrame.from_records([new_row])
        self.skill_summary = pd.concat([self.skill_summary, new_row_df])
        self.skill_summary.fillna(0, inplace=True)


def find_entity_index(entities_list, name):
    """
        returns the index of the entity whose name is passed in parameter
        if not present, creates it then returns the index
    """
    if entities_list == []:
            index = 0
            entities_list.append(Entity(name))
    else:
        i=0
        found = False
        while (i != len(entities_list)) and not found:
            if entities_list[i].name == name:
                index = i
                found = True
            else: 
                i+=1
        if not found:
            index = len(entities_list)
            entities_list.append(Entity(name))
    return index




def treat_line(line, current_entities_list, current_entity_index, skill, verbose=False):
    line = line[11:-2] # Enlever l'heure et le \n

    end_battle = False
    # fin du combat
    if re.search(r'fin de combat', line) is not None:
        if verbose:
            print(f"Battle {combat_number} end")
        end_battle = True

    # skill cast
    elif re.search(r' lance ', line) is not None:
        # skill cast form : ' Caster lance Skill'
        line_split = re.split(' lance ', line)
        caster = line_split[0]
        skill = line_split[1]
        CC = re.search(r". Coup critique", skill)
        if CC is not None:
            skill = skill[:CC.start()]
            
        if verbose:
            print(f'skill_cast : {caster} - {skill}')

        # search if caster is new or existing
        if current_entities_list == []:
            current_entity_index = 0
            current_entities_list.append(Entity(caster))
        else:
            i=0
            found = False
            while (i != len(current_entities_list)) and not found:
                if current_entities_list[i].name == caster:
                    current_entity_index = i
                    found = True
                else: 
                    i+=1
            if not found:
                current_entity_index = len(current_entities_list)
                current_entities_list.append(Entity(caster))

    elif re.search(r' déclenche ', line) is not None:
        caster = re.split(' de ', line)[-1]
        str_skill = line[:re.search(' de '+ caster, line).start()]
        skill = re.split(' déclenche ', str_skill)[1]

        if verbose:
            print(f'skill_cast : {caster} - {skill}')

        # search if caster is new or existing
        if current_entities_list == []:
            current_entity_index = 0
            current_entities_list.append(Entity(caster))
        else:
            i=0
            found = False
            while (i != len(current_entities_list)) and not found:
                if current_entities_list[i].name == caster:
                    current_entity_index = i
                    found = True
                else: 
                    i+=1
            if not found:
                current_entity_index = len(current_entities_list)
                current_entities_list.append(Entity(caster))
    # Skill effect
    else:
        line_split = re.split(' : ', line)
        if len(line_split)>=2:
            targets = re.split(', ', line_split[0])
            effect_raw = line_split[1]
            if 'PV.' in effect_raw :
                if '-' in effect_raw:
                    effect = 'damage'
                    value = re.search(r"[0-9]+", effect_raw)[0]
                    for target in targets:
                        current_entities_list[current_entity_index].add_action(skill, effect, value, target)
                else:
                    effect = 'heal received'
                    value = re.search(r"[0-9]+", effect_raw)[0]
                    for target in targets:
                        current_entities_list[current_entity_index].add_action(skill, effect, value, target)
                        target_index = find_entity_index(current_entities_list, target)
                        current_entities_list[target_index].add_action(skill, effect, value, target)
                if verbose:
                    print(f'skill_effect : {skill, effect, int(value), target}')

            elif ('PB.' in effect_raw) or ('Bouclier' in effect_raw):
                if '-' in effect_raw:
                    effect = 'damage'
                    value = re.search(r"[0-9]+", effect_raw)[0]
                    for target in targets:
                        current_entities_list[current_entity_index].add_action(skill, effect, value, target)
                else:
                    effect = 'shield received'
                    value = re.search(r"[0-9]+", effect_raw)[0]
                    for target in targets:
                        target_index = find_entity_index(current_entities_list, target)
                        current_entities_list[target_index].add_action(skill, effect, value, target)
                if verbose:
                    print(f'skill_effect : {skill, effect, int(value), target}')
            
    return current_entities_list, current_entity_index, skill, end_battle


################################
### streamlit initialization ###
################################

st.set_page_config(page_title="Dofus KIKI meter", layout="wide")

st.title("Dofus KIKI meter")

with st.expander("How to start"):
    st.write("\nFirst you need to open the external chat window :")
    col1, col2 = st.columns(2)
    col1.image("tutorial_images/menu_click.png")
    col2.image("tutorial_images/open_chat.png")
    st.write("Then select only the combat channel and clear the chat :")
    col1, col2 = st.columns(2)
    col1.image("tutorial_images/select_channel.png")
    col2.image("tutorial_images/click_eraser.png")
    st.write("After one or more combat, click on the save icon to download the .txt file :")
    st.image("tutorial_images/save_log.png")
    st.write("Then you are good to go ! Just put your file in the widget below !")

combat_log = st.file_uploader("Select combat logs")

if combat_log is not None:
    combat_log = combat_log.getvalue().decode("utf-8")
    combat_log = re.split('\n', combat_log)

    ################################
    ### parsing and calculations ###
    ################################


    combat_entity_list = []
    current_entities_list = []
    current_entity_index = None
    skill = None
    combat_number = 0
    for l in combat_log: 
        current_entities_list, current_entity_index, skill, end_battle = treat_line(l, current_entities_list, current_entity_index, skill)
        if end_battle:
            combat_entity_list.append(current_entities_list)
            current_entities_list = []
            current_entity_index = None
            skill = None
            combat_number += 1
            
    if combat_number == 0:
        st.warning("Warning : No text 'fin de combat' detected, all the logs will be considered as a single combat")
        combat_entity_list.append(current_entities_list)
        current_entities_list = []
        current_entity_index = None
        skill = None
        combat_number += 1

    with st.sidebar:
        st.title("Combat selection")
        combat_number = st.selectbox("Select combat", [i for i in range(1, len(combat_entity_list)+1)],
                                      help="For a combat to be detected, the file needs to have the 'fin de combat' line at the end of each combat")
        entities_list = combat_entity_list[combat_number-1]


    total = pd.DataFrame(columns=["Entity", "damage", "heal received", "shield received"])
    detailed_figs = []
    for i in entities_list:
        # detailed damage stats
        per_skill_damage = i.skill_summary
        per_skill_damage = per_skill_damage.astype({"damage":int, "heal received":int, "shield received":int})
        per_skill_damage = per_skill_damage.groupby("skill").sum()
        per_skill_damage.sort_values(by="damage", inplace = True)

        new_row_total = {"Entity":i.name,
                        "damage":per_skill_damage["damage"].sum(), 
                        "heal received":per_skill_damage["heal received"].sum(), 
                        "shield received":per_skill_damage["shield received"].sum()}
        new_row_df_total = pd.DataFrame.from_records([new_row_total])
        total = pd.concat([total, new_row_df_total]).astype({"damage":int, "heal received":int, "shield received":int})

        per_skill_damage = per_skill_damage.replace(0, np.nan).dropna(axis=0, how='all')
        # per_skill_damage = per_skill_damage[['damage', 'heal received', 'shield received']].replace(0, np.nan).dropna(axis=0)
        # per_skill_damage.rename(columns={"damage":"Damage", "heal received":"Heal given", "shield received":"Shield given"}, inplace=True)
        print(f"\n ==={i.name}===")
        print(per_skill_damage)
        if per_skill_damage.shape[0]!=0:
            fig = px.bar(per_skill_damage, title=i.name, barmode='group', text_auto=True, orientation ='h')
            fig.update_layout(xaxis_title="Total",
                    yaxis_title="Skill",
                    legend_title="Type",
                    hovermode="y unified")
            fig.update_traces(hovertemplate='<b>%{x}</b>')
            detailed_figs.append(fig)

    total.set_index("Entity", inplace=True)
    total.sort_values(by="damage", inplace = True)
    total = total.replace(0, np.nan).dropna(axis=0, how='all')

    ################################
    ###     plotting results     ###
    ################################

    st.header("Global statistics")
    fig = px.bar(total,
                barmode='group',
                text_auto=True,
                title="Total contribution",
                orientation ='h', height=700)
    fig.update_layout(xaxis_title="Total",
                    yaxis_title="Entity",
                    legend_title="Type",
                    hovermode="y unified")
    fig.update_traces(hovertemplate='<b>%{x}</b>')
    st.plotly_chart(fig,
                    use_container_width=True)
    st.header("Detailed infos")
    col1, col2 = st.columns(2)
    cols=[col1, col2]
    i=0
    for f in detailed_figs:
        cols[i%2].plotly_chart(f)
        i+=1
