import requests
import xml.etree.ElementTree as ET
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from emanifest import new_client
from emanifest import RcrainfoClient
from emanifest import RcrainfoResponse
from Epa_Data_Calls import ApiUrl, AZ_RcraClient
from PIL import ImageTk, Image

class EpaDataForm:
    def __init__(self):
        '''
        Desc: Initialize data form and user variables
        '''
        self.root=tk.Tk()
        self.root.title("Epa Data Form")
        self.root.configure(bg="#e2d7c9")
        self.form_type_var = tk.StringVar(self.root)
        self.api_id_entry = None
        self.api_key_label = None
        self.api_key_entry = None
        self.site_id_entry = None
        self.facility_type_var = tk.StringVar(self.root)
        self.change_date_entry = None
        self.start_date_entry = None
        self.end_date_entry = None
        self.site_class_var = tk.StringVar(self.root)
        self.file_choice_var = tk.StringVar(self.root)
        self.date_type_var = tk.StringVar(self.root)
        self.nrr_flag_var = tk.StringVar(self.root)
        self.regulator_endpoint_var = tk.StringVar(self.root)
        self.state_entry = None
        self.agency_entry = None
        self.details_var = tk.StringVar(self.root)
        self.source_type_entry = None
        self.sequence_number_entry = None
        self.state_id_entry = None
        self.create_form()
    
    def show(self):
        '''
        Desc: Display initalized user entry data form
        '''
        self.root.mainloop()

    def create_form(self):
        '''
        Desc: Create forms and entry fields
        '''
        # creates user form structure
        main_frame = tk.Frame(self.root, bg='#e2d7c9')
        main_frame.pack(fill="both", expand=True)

        # create teal header frame
        header_frame = tk.Frame(main_frame, bg="#5c8985")
        header_frame.grid(row=0, column=0, columnspan=3, rowspan=2, sticky='nsew')

        # input adeq logo
        img = ImageTk.PhotoImage(Image.open("logo_smaller.png"))
        header_label = tk.Label(main_frame, image=img, bg="#5c8985")
        header_label.grid(row=0, columnspan=3)
        header_label.image = img 

        # create form title 
        title_label = tk.Label(main_frame, text="EPA DATA REQUEST", bg="#5c8985", fg="white", font=("Oswald", 22))
        title_label.grid(row=1, columnspan=3, pady=5)


        labels = {}

        #Data Request Type
        form_type_label = tk.Label(main_frame, text="Choose request type:", bg="#e2d7c9", font=("Oswald", 12))
        form_type_label.grid(row=2, column=1, pady=5, sticky="w")
        form_type_dropdown = ttk.Combobox(main_frame, textvariable=self.form_type_var,
                                          values = ['<choose query type>', 'GetManifestData', 'GetCEDataByHandler', 
                                                    'GetCADataByHandler', 'GetFADataByHandler', 'GetGSDataByHandler',
                                                    'GetHDDataByHandler', 'GetHDMaxSequence', 'GetCurrentHandlerById',
                                                    'GetTransportersData', 'GetHandlerRecords', 'GetCMELookups', 
                                                    'GetSiteDetails'], state="readonly")
        form_type_dropdown.current(0)
        form_type_dropdown.grid(row=2, column=2, pady=5)
        self.form_type_var.trace_add('write', lambda name, index, mode: self.conditional_form_entries(labels)) # calls conditional_form_entries whenever form type is changed by user

        # User API ID Entry
        labels['apiId'] = tk.Label(main_frame, text="Enter your RCRAInfo API ID:", bg="#e2d7c9", font=("Oswald", 12)) # create label and assigns it to a dictionary
        labels['apiId_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12)) # create the red required astreik and assigns it to a dictionary
        self.api_id_entry = tk.Entry(main_frame, font=("Oswald", 12)) # create the user entry form and assigns it to a class object

        # API Key Entry
        api_key_label = tk.Label(main_frame, text="Enter your API key:", bg="#e2d7c9", font=("Oswald", 12))
        labels['apiKey'] = api_key_label
        labels['apiKey_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.api_key_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # SiteID Entry
        site_id_label = tk.Label(main_frame, text="Enter your SiteID:", bg="#e2d7c9", font=("Oswald", 12))
        labels['siteId'] = site_id_label
        labels['siteId_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.site_id_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # Facility Type Dropdown
        facility_type_label = tk.Label(main_frame, text="Choose your facility type:", bg="#e2d7c9", font=("Oswald", 12))
        labels['facilityType'] = facility_type_label
        labels['facilityType_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.facility_type_dropdown = ttk.Combobox(main_frame, textvariable=self.facility_type_var, 
                                                   values=['Generator', 'Tsdf', 'Transporter', 'RejectionInfo_AlternateTsdf'], 
                                                   state="readonly")

        # For Date Type Dropdown
        date_type_label = tk.Label(main_frame, text="Choose your date type:", bg="#e2d7c9", font=("Oswald", 12))
        labels['dateType'] = date_type_label
        labels['dateType_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.date_type_dropdown = ttk.Combobox(main_frame, textvariable=self.date_type_var, values=['CertifiedDate', 'ReceivedDate', 'ShippedDate', 'UpdatedDate'], state="readonly")

        # create change date label and entry box
        change_date_label = tk.Label(main_frame, text="Enter your change date (yyyy-MM-dd):", bg="#e2d7c9", font=("Oswald", 12))
        labels['cD'] = change_date_label
        self.change_date_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # create start date label and entry box
        start_date_label = tk.Label(main_frame, text="Enter your start date (yyyy-MM-dd):", bg="#e2d7c9", font=("Oswald", 12))
        labels['sD'] = start_date_label
        labels['sD_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.start_date_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # create end date label and entry box
        end_date_label = tk.Label(main_frame, text="Enter your end date (yyyy-MM-dd):", bg="#e2d7c9", font=("Oswald", 12))
        labels['eD'] = end_date_label
        labels['eD_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.end_date_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # create state label and entry box
        state_label = tk.Label(main_frame, text="Enter your state (Two-Letter Postal Code - i.e. AZ):", bg="#e2d7c9", font=("Oswald", 12))
        labels['state'] = state_label
        self.state_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # create agency label and entry box
        agency_label = tk.Label(main_frame, text="Enter your agency:", bg="#e2d7c9", font=("Oswald", 12))
        labels['agency'] = agency_label
        self.agency_entry = tk.Entry(main_frame, font=("Oswald", 12))

        site_class_label = tk.Label(main_frame, text="Select site type", bg="#e2d7c9", font=("Oswald", 12))
        labels['site_class'] = site_class_label
        self.site_class_dropdown = ttk.Combobox(main_frame, textvariable=self.site_class_var, values=['B - State Contractor', 'C - EPA Contractor',
                                                                                                        'E - EPA', 'L - Local', 'N - Native American',
                                                                                                        'S - State', 'T - State-Initiated Oversight/Observation',
                                                                                                        'X - EPA-Initated Oversight/Observation', 'J - Joint State',
                                                                                                        'P - Joint EPA'])
        self.site_class_dropdown.current(0)

        # create source type label and entry box
        source_type_label = tk.Label(main_frame, text="Enter your source type:", bg="#e2d7c9", font=("Oswald", 12))
        labels['sT'] = source_type_label
        self.source_type_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # create sequence number label and entry box
        sequence_number_label = tk.Label(main_frame, text="Enter your sequence number:", bg="#e2d7c9", font=("Oswald", 12))
        labels['sN'] = sequence_number_label
        self.sequence_number_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # create user input for Non-Financial Record Review access
        nrr_flag_label = tk.Label(main_frame, text="Access only the Non-Financial record review?", bg="#e2d7c9", font=("Oswald", 12))
        labels['nrr'] = nrr_flag_label
        self.nrr_flag_dropdown = ttk.Combobox(main_frame, values = ["Yes", "No"], textvariable=self.nrr_flag_var, state="readonly")
        self.nrr_flag_dropdown.current(0)

        # create user input to access handler details
        details_label = tk.Label(main_frame, text='Access Additional Details?', bg="#e2d7c9", font=("Oswald", 12))
        labels['details'] = details_label
        self.details_dropdown = ttk.Combobox(main_frame, values = ["No", "Yes"], textvariable=self.details_var, state="readonly")
        self.details_dropdown.current(0)

        #choose regulator status
        regulator_endpoint_label = tk.Label(main_frame, text="Use regulator endpoint", bg="#e2d7c9", font=("Oswald", 12))
        labels['reg'] = regulator_endpoint_label
        self.regulator_endpoint_dropdown = ttk.Combobox(main_frame, values = ["Yes", "No"], textvariable=self.regulator_endpoint_var, state="readonly")
        self.regulator_endpoint_dropdown.current(0)

        # create state id label and entry box
        state_id_label = tk.Label(main_frame, text="Enter your state ID:", bg="#e2d7c9", font=("Oswald", 12))
        labels['stateId'] = state_id_label
        self.state_id_entry = tk.Entry(main_frame, font=("Oswald", 12))

        # create user input 
        file_type_label = tk.Label(main_frame, text="Choose File Format:", bg="#e2d7c9", font=("Oswald", 12))
        labels['fileType'] = file_type_label
        labels['fileType_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.file_choice_dropdown = ttk.Combobox(main_frame, textvariable=self.file_choice_var, values=['<choose file type>', 'Excel'], state="readonly")
        self.file_choice_dropdown.current(0)

        # create file path
        file_path_label = tk.Label(main_frame, text="Enter your File Path to Save Data Here:", bg="#e2d7c9", font=("Oswald", 12))
        labels['filePath'] = file_path_label
        labels['filePath_asterik'] = tk.Label(main_frame, text='*', fg='red', bg="#e2d7c9", font=("Oswald", 12))
        self.file_path_entry = tk.Entry(main_frame, font=("Oswald", 12))

        #Submit Button
        submit_button = tk.Button(main_frame, text="       Submit       ", command=self.submit_form, bg="#5c8985", fg="black", font=("Oswald", 12))
        labels['submit'] = submit_button

    def form_categories(self):
        '''
        Desc: create dictionary with lists of entry fields included in each
        request type
        Return:
            dct: dict object containing form entry fields
        '''
        dct = {
            'GetCEDataByHandler': [ 'siteId', 'state', 'agency', 'cD'], 
            'GetCADataByHandler': [ 'siteId', 'cD'],
            'GetFADataByHandler': [ 'siteId', 'cD'],
            'GetGSDataByHandler': [ 'siteId', 'cD'],
            'GetHDDataByHandler': [ 'siteId', 'cD', 'state', 'sT', 'sN'],
            'GetHDMaxSequence': [ 'siteId', 'sT', 'stateId'],
            #'GetHDDataByFedFac': ['apiId', 'apiKey', 'sD', 'eD'],
            'GetCurrentHandlerById': [ 'siteId', 'cD'],
            '<choose query type>': [],
            'GetManifestData': ['apiId', 'apiKey', 'siteId', 'facilityType', 'dateType', 'sD', 'eD'],
            'GetTransportersData': ['apiId', 'apiKey', 'siteId', 'dateType', 'sD', 'eD'],
            'GetHandlerRecords' : ['apiId', 'apiKey', 'siteId',  'details'],
            'GetCMELookups' : ['apiId', 'apiKey', 'siteId',  'state', 'site_class', 'nrr'],
            'GetSiteDetails' : ['apiId', 'apiKey', 'siteId']
            #'GetPMDataByHandler': ['siteId', 'facilityType', 'dateType', 'cD']
        }
        return dct

    def submit_form(self):
        '''
        Desc: gets api data when submit button pressed
        Parameters:
            self - EpaRestData object
        return: None
        '''

        # assign user entries to variables
        form_type_str = self.form_type_var.get()
        api_key = self.api_key_entry.get()
        api_id = self.api_id_entry.get()
        site_id = self.site_id_entry.get()
        date_type = self.date_type_var.get()
        facility_type = self.facility_type_var.get()
        change_date_str = self.change_date_entry.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        state_str = self.state_entry.get()
        agency_str = self.agency_entry.get()
        change_date_str = self.change_date_entry.get()
        state_id_str = self.state_id_entry.get()
        source_type_str = self.source_type_entry.get()
        regulator_endpoint_bool = self.regulator_endpoint_var.get()
        site_class_str = self.site_class_var.get()
        nrr_flag_bool = self.nrr_flag_var.get()
        details_bool = self.details_var.get()
        sequence_number_str = self.sequence_number_entry.get()
        file_type = self.file_choice_var.get()
        file_path = self.file_path_entry.get()

        # assign boolean user entries to Bool Objects
        if regulator_endpoint_bool =='Yes':
            regulator_endpoint_bool=True
        else:
            regulator_endpoint_bool=False
        
        if nrr_flag_bool=='Yes':
            nrr_flag_bool=True
        else:
            nrr_flag_bool=False
        
        if details_bool=='Yes':
            details_bool=True
        else:
            details_bool=False

        if site_class_str:
            site_class_str = site_class_str.split('-')[0].strip()

        # Check for missing required values
        dct = self.form_categories()[form_type_str] # get categories of required values
        
        if 'apiId' in dct and not api_id:
            messagebox.showwarning("Warning", "Api ID must be provided. Please provide a valid RCRAInfo API ID.")
            return
        
        if 'apiKey' in dct and not api_key:
            messagebox.showwarning("Warning", "API Key must be provided. Please provide a valid RCRAInfo API Key")
            return
        
        if 'siteId' in dct and not site_id:
            messagebox.showwarning("Warning", "Site ID must be provided. Please provide a valid EPAID.")
            return

        if 'facilityType' in dct and not facility_type:
            messagebox.showwarning("Warning", "Facility type must be provided. Please select a facility type.")
            return
        
        if 'dateType' in dct and not date_type:
            messagebox.showwarning("Warning", "Facility type must be provided. Please select a facility type.")
            return

        # Check both presence and validity of dates provided
        if 'sD' in dct:
            if not start_date_str:
                messagebox.showwarning("Warning", "Start Date must be provided. Please enter start date in yyyy-mm-dd format.")
                return
            if not end_date_str:    
                messagebox.showwarning("Warning", "End Date must be provided. Please enter end date in yyyy-mm-dd format.")
                return
            date_format = '%Y-%m-%d'
            try:
                start_date = datetime.strptime(start_date_str, date_format)
                end_date = datetime.strptime(end_date_str, date_format)
                if end_date < start_date:
                    messagebox.showerror("Error", "End date must be after start date.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter dates in 'yyyy-MM-dd' format.")
                return None

        if change_date_str:
                date_format = '%Y-%m-%d'
                try:
                    change_date = datetime.strptime(change_date_str, date_format)
                except ValueError: # error messagebox if date entered in wrong format
                    messagebox.showerror("Error", "Please enter dates in the yyyy-mm-dd format.")

        if file_type == '<choose file type>':
            messagebox.showwarning("Warning", "File type must be provided. Please select a file type from the dropdown")
            return None
        
        if not file_path:
            messagebox.showwarning("Warning", "File path must be provided. Please enter a valid file path to save the data file at.")
            return None

        try:
            # If chosen type is ApiUrl object, get data object from ApiUrl
            if form_type_str not in ['GetManifestData', 'GetTransportersData', 'GetHandlerRecords', 'GetCMELookups', 'GetSiteDetails']:
                    
                # create ApiUrl object and assign variables to it
                epa_url = ApiUrl(self.form_type_var.get(), site_id)
                epa_url.startDate = start_date_str
                epa_url.endDate = end_date_str
                epa_url.state = state_str
                epa_url.agency = agency_str
                epa_url.changeDate = change_date_str
                epa_url.stateId = state_id_str
                epa_url.sourceType = source_type_str
                epa_url.sequenceNumber = sequence_number_str
                epa_url.file_path = file_path

                data, content_flag  = ApiUrl.get_api_data(epa_url) # get data from api link

                if not content_flag: # throw up warning if data is empty
                    messagebox.showwarning("Warning", "Request did not return data. Widen request parameters.")
                    return None  
            
            # If form type is from RCRA client, get Az_RcraClient data
            else:
                epa_client = AZ_RcraClient(api_id, api_key)
                if not epa_client.client.is_authenticated:
                    epa_client.client.authenticate()

                if not epa_client.client.is_authenticated:
                    messagebox.showwarning("API Authentication Failed", "Your request failed to meet the EPA API Authentication requirements. Please check your API ID and Key, and try again. If your API ID is correct, try regenerating a new key in RCRAinfo under Tools -> Translation/API Maintenance -> Manage API.")
                    return None

                else:

                    # select client request
                    if form_type_str == 'GetManifestData':
                        data = epa_client.get_mmanifests_short(site_id, facility_type, date_type, start_date_str, end_date_str)
                    elif form_type_str == 'GetTransportersData':
                        data = epa_client.get_mtransporter(site_id, date_type, start_date_str, end_date_str)
                    elif form_type_str == 'GetHandlerRecords':
                        data = epa_client.get_handler_df(handler_id=site_id, details=details_bool)
                    elif form_type_str == 'GetCMELookups':
                        data = epa_client.get_cme_lookup_df(site_type=site_class_str, state=state_str, nrr_flag=nrr_flag_bool)
                    else:
                        data = epa_client.get_site_details(handler_id=site_id)

            if file_type == 'Excel':
                self.create_excel(data, file_path, form_type_str, site_id)

        except Exception as e:
            messagebox.showerror("Error", e)
    
    def create_excel(self, data, file_path, query_type, siteId):
        '''
        Desc: Take data object and save it as an .xlsx file to the specified location
        Parameters:
            data - dict of dfs, df or list containing information from the specified query
            file_path - str representing the directory path to save file to
            query_type - str representing query type
            siteId - str representing siteId
        '''
        current_time = datetime.now()
        current_time_str = current_time.strftime('%Y-%m-%d_%H%M%S')

        if isinstance(data, dict): # run following code if data is a dictionary of dataframes
            with pd.ExcelWriter(f'{file_path}/{query_type}_{siteId}_{current_time_str}.xlsx', engine='xlsxwriter') as writer:
                for k, v in data.items():
                    df = pd.DataFrame(v)
                    df.to_excel(writer, sheet_name=k, index=False)
        elif isinstance(data, list): # run following code if data is a list
            list_df = pd.DataFrame(data)
            list_df.to_excel(f'{file_path}/{query_type}_{siteId}_{current_time_str}.xlsx', index=False, engine='xlsxwriter')
        else: # run following code otherwise (data is a dataframe)
            data.to_excel(f'{file_path}/{query_type}_{siteId}_{current_time_str}.xlsx', index=False, engine='xlsxwriter')

        messagebox.showinfo("Info", f"Data saved to {file_path}/{query_type}_{siteId}_{current_time_str}.xlsx")

        return None

    
         

    def conditional_form_entries(self, labels):
        '''
        Desc: show entry boxes depending on query type
        Parameters: 
            self - EpaRestData object
            labels - dct object with label form data
        Return: None
        '''
        y=3

        #reset the form to default
        self.site_id_entry.config(state='normal')

        labels['apiId'].grid_forget()
        labels['apiId_asterik'].grid_forget()
        self.api_id_entry.grid_forget()

        labels['apiKey'].grid_forget()
        labels['apiKey_asterik'].grid_forget()
        self.api_key_entry.grid_forget()

        labels['siteId'].grid_forget()
        labels['siteId_asterik'].grid_forget()
        self.state_id_entry.grid_forget()

        labels['facilityType'].grid_forget()
        labels['facilityType_asterik'].grid_forget()
        self.facility_type_dropdown.grid_forget()

        labels['dateType'].grid_forget()
        labels['dateType_asterik'].grid_forget()
        self.date_type_dropdown.grid_forget()

        labels['cD'].grid_forget()
        self.change_date_entry.grid_forget()

        labels['state'].grid_forget()
        self.state_entry.grid_forget()

        labels['agency'].grid_forget()
        self.agency_entry.grid_forget()

        labels['sD'].grid_forget()
        labels['sD_asterik'].grid_forget()
        self.start_date_entry.grid_forget()

        labels['eD'].grid_forget()
        labels['eD_asterik'].grid_forget()
        self.end_date_entry.grid_forget()

        labels['sT'].grid_forget()
        self.source_type_entry.grid_forget()

        labels['sN'].grid_forget()
        self.sequence_number_entry.grid_forget()

        labels['stateId'].grid_forget()
        self.state_id_entry.grid_forget()

        labels['nrr'].grid_forget()
        self.nrr_flag_dropdown.grid_forget()

        labels['site_class'].grid_forget()
        self.site_class_dropdown.grid_forget()

        labels['details'].grid_forget()
        self.details_dropdown.grid_forget()

        labels['reg'].grid_forget()
        self.regulator_endpoint_dropdown.grid_forget()

        labels['fileType'].grid_forget()
        self.file_choice_dropdown.grid_forget()

        labels['filePath'].grid_forget()
        self.file_path_entry.grid_forget()

        labels['submit'].grid_forget()

        # creates a dct with information about what textboxes are in the form
        dct = self.form_categories()

        # select query type form to make
        form_entries = dct[self.form_type_var.get()]

        if 'apiId' in form_entries:
            labels['apiId'].grid(row=y, column=1, pady=5, padx = (1,0), sticky="w")
            labels['apiId_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
            self.api_id_entry.grid(row=y, column=2, pady=5)
            y+=1
        
        if 'apiKey' in form_entries:
            labels['apiKey'].grid(row=y, column=1, pady=5, sticky="w")
            labels['apiKey_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
            self.api_key_entry.grid(row=y, column=2, pady=5)
            y+=1

        # activate forms depending on query type
        if 'siteId' in form_entries:
            labels['siteId'].grid(row=y, column=1, pady=5, sticky="w")
            labels['siteId_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
            self.site_id_entry.grid(row=y, column=2, pady=5)
            y+=1

        if 'facilityType' in form_entries:
            labels['facilityType'].grid(row=y, column=1, pady=5, sticky="w")
            labels['facilityType_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
            self.facility_type_dropdown.grid(row=y, column=2, pady=5)
            y+=1

        if 'dateType' in form_entries:
            labels['dateType'].grid(row=y, column=1, pady=5, sticky="w")
            labels['dateType_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
            self.date_type_dropdown.grid(row=y, column=2, pady=5)
            y+=1

        if 'cD' in form_entries:
            labels['cD'].grid(row=y, column=1, pady=5, sticky="w")
            self.change_date_entry.grid(row=y, column=2, pady=5)
            y+=1       

        if 'sD' in form_entries:
            labels['sD'].grid(row=y, column=1, pady=5, sticky="w")
            labels['sD_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
            self.start_date_entry.grid(row=y, column=2, pady=5)
            y += 1  

        if 'eD' in form_entries:
            labels['eD'].grid(row=y, column=1, pady=5, sticky="w")
            labels['eD_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
            self.end_date_entry.grid(row=y, column=2, pady=5)
            y += 1

        if 'state' in form_entries:
            labels['state'].grid(row=y, column=1, pady=5, sticky="w")
            self.state_entry.grid(row=y, column=2, pady=5)
            y += 1
        
        if 'agency' in form_entries:
            labels['agency'].grid(row=y, column=1, pady=5, sticky="w")
            self.agency_entry.grid(row=y, column=2, pady=5)
            y += 1     
        
        if 'sT' in form_entries:
            labels['sT'].grid(row=y, column=1, pady=5, sticky="w")
            self.source_type_entry.grid(row=y, column=2, pady=5)
            y += 1
        
        if 'sN' in form_entries:
            labels['sN'].grid(row=y, column=1, pady=5, sticky="w")
            self.sequence_number_entry.grid(row=y, column=2, pady=5)
            y += 1
        
        if 'stateId' in form_entries:
            labels['stateId'].grid(row=y, column=1, pady=5, sticky="w")
            self.state_id_entry.grid(row=y, column=2, pady=5)
            y += 1

        if 'site_class' in form_entries:
            labels['site_class'].grid(row=y, column=1, pady=5, sticky="w")
            self.site_class_dropdown.grid(row=y, column=2, pady=5)
            y += 1

        if 'reg' in form_entries:
            labels['reg'].grid(row=y, column=1, pady=5, sticky="w")
            self.regulator_endpoint_dropdown.grid(row=y, column=2, pady=5)
            y += 1
        
        if 'nrr' in form_entries:
            labels['nrr'].grid(row=y, column=1, pady=5, sticky="w")
            self.nrr_flag_dropdown.grid(row=y, column=2, pady=5)
            y += 1
        
        if 'details' in form_entries:
            labels['details'].grid(row=y, column=1, pady=5, sticky="w")
            self.details_dropdown.grid(row=y, column=2, pady=5)
            y += 1

        labels['fileType'].grid(row=y, column=1, pady=5, sticky="w")
        labels['fileType_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
        self.file_choice_dropdown.grid(row=y, column=2, pady=5)
        y+=1

        labels['filePath'].grid(row=y, column=1, pady=5, sticky="w")
        labels['filePath_asterik'].grid(row=y, column=0, pady=5, padx=(0, 5))
        self.file_path_entry.grid(row=y, column=2, pady=5)
        y+=1

        labels['submit'].grid(row=y, columnspan=3, pady=5)

        if self.form_type_var.get() == '<choose query type>':
            labels['fileType'].grid_forget()
            labels['fileType_asterik'].grid_forget()
            self.file_choice_dropdown.grid_forget()

            labels['filePath'].grid_forget()
            labels['filePath_asterik'].grid_forget()
            self.file_path_entry.grid_forget()

            self.site_id_entry.grid_forget()
            labels['submit'].grid_forget()
        
    

def main():
    # create EpaDataFrom and display it when the code is run
    site = EpaDataForm()
    site.show()

if __name__ == '__main__':
    main()
