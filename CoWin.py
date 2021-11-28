import streamlit as st
import requests
import datetime

center_id = []

def name_generator(names_length):
    names = []
    for i in range(names_length):
        names.append('key'+str(i))
    return names

@st.cache
def states():
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    state = requests.get(url=url)
    states_dict ={}
    for x in range(len(state.json()['states'])):
        states_dict[state.json()['states'][x]['state_name']] = state.json()['states'][x]['state_id']
    return states_dict

@st.cache
def districts(states_dict, select_state):
    dist_url ="https://cdn-api.co-vin.in/api/v2/admin/location/districts/"
    dist_url= dist_url + str(states_dict[select_state])
    district = requests.get(url=dist_url)

    result=district.json()
    dist_list = {}
    for x in range(len(result['districts'])):
        #dist = result['districts'][x]['district_name']
        dist_list[result['districts'][x]['district_name']] = result['districts'][x]['district_id']
    return dist_list

@st.cache
def centers(dist_dict, select_dist):
    appoint_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id="
    appoint_url =  appoint_url + str(dist_dict[select_dist]) + "&date=" + start_date
    dist_center = requests.get(url=appoint_url)
    temp = dist_center.json()
    centers_names = {}
    centers_names_pin = {}
    for x in range(len(temp['centers'])):
        session = temp['centers'][x]['sessions']
        centers_names[temp['centers'][x]['name']] = temp['centers'][x]['center_id']
        centers_names_pin[temp['centers'][x]['name']] = temp['centers'][x]['pincode']
    return centers_names, centers_names_pin, temp

def center_details(centers_names, center, start_date):
    center_url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByCenter?center_id='
    center_url = center_url + str(centers_names[center]) + "&date=" + start_date
    center_avail = requests.get(url=center_url)
    return center_avail.json()

def details(cntr_details):
    #st.write(cntr_details['centers']['sessions'])
    if st.session_state.search == 'By Pin' or st.session_state.select_center == "Select Center":
        for y in range(len(cntr_details['centers'])):
            temp1=cntr_details['centers'][y]['sessions']
            
            details_print(cntr_details['centers'][y], temp1)

    elif st.session_state.search == 'By District':
            temp1 = cntr_details['centers']['sessions']
            details_print(cntr_details, temp1)


def details_print(cntr_details, temp1):
   
    if st.session_state.search == "By Pin" or st.session_state.select_center == "Select Center":
        center_id.append(cntr_details['center_id'])
        center_add = "Center Address : " + cntr_details['address'] +", " + cntr_details['district_name'] + ", " +cntr_details['state_name'] + ", Pin-" + str(cntr_details['pincode'])
        paid_type = cntr_details['fee_type']
        cent_name = cntr_details['name']
        
    elif st.session_state.search == "By District":
        center_add = "Center Address : " + cntr_details['centers']['address'] +", " + cntr_details['centers']['district_name'] + ", " +cntr_details['centers']['state_name'] + ", Pin-" + str(cntr_details['centers']['pincode'])
        paid_type = cntr_details['centers']['fee_type']
        cent_name = cntr_details['centers']['name']

    try:
        if st.session_state.select_center == "Select Center":
            T_F= False
        else:
            T_F=True
    except:
        if len(center_id) == 1:
            T_F = True
        else:
            T_F = False

    
    with st.expander(cent_name, expanded=T_F):

        st.write('Center Address : ',center_add )
        st.write("Paid Type : ", paid_type)
        st.write('---')
        for x in range(len(temp1)):
            if temp1[x]['min_age_limit'] == 18 or temp1[x]['min_age_limit'] == 45:
                date = temp1[x]['date'] + ' | Minimum Age : ' + str(temp1[x]['min_age_limit'])
                doses = 'D1 : '+ str(temp1[x]['available_capacity_dose1']) + ' | D2 : ' +  str(temp1[x]['available_capacity_dose2']) + ' | Total : ' + str(temp1[x]['available_capacity'])
                if temp1[x]['available_capacity'] == False:
                    vaccine_name =  "-"+temp1[x]['vaccine'] + " BOOKED"
                    st.metric(date,doses,vaccine_name, delta_color='normal')
                elif temp1[x]['available_capacity'] > 0:
                    vaccine_name = temp1[x]['vaccine']
                    st.metric(date,doses,vaccine_name, delta_color='normal')

##### Main Function from here
st.title("Vaccine Slot Notifier App")
st.sidebar.selectbox("Search By:",["By District","By Pin"], key = 'search', index=1)
date = datetime.datetime.today()
start_date= str(date.day) + "-" + str(date.month) + "-" + str(date.year)


if st.session_state.search == 'By District':
    states_dict = states()
    state_list = list(states_dict.keys())
    state_list.sort()
    select_state = st.sidebar.selectbox("State", state_list,index=34)
    dist_dict = districts(states_dict, select_state)
    dist_list= list(dist_dict.keys())
    dist_list.sort()
    select_dist = st.sidebar.selectbox("District",dist_list, index=16)
    centers_names, centers_names_pin, dist_centers_details = centers(dist_dict, select_dist)
    add_name = ["Select Center"]
    centers_names_final = list(centers_names.keys())
    centers_names_final.sort()
    centers_names_final = add_name + centers_names_final
    center = st.sidebar.selectbox("Center",centers_names_final, key='select_center', index=0)
    if center != 'Select Center':
        cntr_details = center_details(centers_names, center, start_date)
        details(cntr_details)
            
    else:
        details(dist_centers_details)

elif st.session_state.search == 'By Pin':
    url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode='
    pincode = st.sidebar.text_input("Enter Pin",max_chars=6,value=272131, key='pin')
    if pincode.isnumeric():
        if len(pincode) < 6:
            st.error("### Invalid Pincode\nEnter ALL 6 digits of area Pincode")
            st.stop()
    else:
        st.error("### Characters are NOT allowed\nTip: Enter 6 digit of area Pincode")
        st.stop()
    #pincode = st.sidebar.number_input("Enter Pin",min_value=100000,max_value=999999,value=272131, key='pin')
    url = url + str(pincode) + "&date=" + start_date
    temp = requests.get(url=url)

    temp1 = temp.json()
    #st.write(temp1['centers'])
    if len(temp1['centers']) == 0:
        st.error("### Incorrect Pincode\nEnter Correct area Pincode")
   
    else:
        details(temp1)
    