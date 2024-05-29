import pandas as pd
from emanifest import new_client
from emanifest import RcrainfoClient
from emanifest import RcrainfoResponse
import requests
import xml.etree.ElementTree as ET
import numpy as np

class ApiUrl:
    def __init__(self, query_type, siteId='', state='', agency='', startDate='', endDate='', changeDate='', sourceType='', sequenceNumber='', stateId=''):
        self.query_type=query_type
        self.siteId=siteId
        self.state=state
        self.agency=agency
        self.startDate=startDate
        self.endDate=endDate
        self.changeDate=changeDate
        self.sourceType=sourceType
        self.sequenceNumber=sequenceNumber
        self.stateId=stateId
        self.url = self.generate_url()
        self.file_path = None

        # check that all required values have been defined
        flag, required_field = self.flag_required_values()
        if flag:
            raise ValueError(f'{self.query_type} queries requires {required_field} to be defined.')
        
        # check that no extraneous values have been defined
        second_flag = self.flag_extraneous_values()
        if second_flag:
            raise ValueError(f'Extraneous values given for query type.')


    def flag_required_values(self):
        '''
        Desc: Determines if a required variable has not been input (currently 
        only checks for siteId but can be modified with more in the future)

        Return:
            boolean value - True if the required values are missing, false if
            not
        '''
        dict = {
                    'GetCADataByHandler':[self.siteId, 'siteId'],
                    'GetCEDataByHandler':[self.siteId, 'siteId'],
                    'GetHDDataByHandler':[self.siteId, 'siteId'],
                    'GetFADataByHandler':[self.siteId, 'siteId'],
                    'GetGSDataByHandler':[self.siteId, 'siteId'],
                    'GetCurrentHandlerById':[self.siteId, 'siteId'],
                    'GetHDMaxSequence':[self.siteId, 'siteId'],
                    'GetHDDataByFedFac':'No required elements',
                    'GetPMDataByHandler':[self.siteId, 'siteId']
        }
        if not dict[self.query_type][0]:
            return True, dict[self.query_type][1]
        return False, dict[self.query_type][1]
    
    def flag_extraneous_values(self):
        '''
        Desc: Create a flag if extraneous values are added to the ApiUrl form type
        Return: Bool values
            True - Extraneous value is present within the object
            False - Extraneous values are not present
        '''
        dict = {
                    'GetCADataByHandler':[self.state, self.agency, self.startDate,
                                          self.endDate, self.sourceType, self.sequenceNumber,
                                          self.stateId],
                    'GetCEDataByHandler':[self.startDate,
                                          self.endDate, self.sourceType, self.sequenceNumber,
                                          self.stateId],
                    'GetHDDataByHandler':[self.agency, self.startDate, self.endDate, 
                                          self.stateId],
                    'GetFADataByHandler':[self.state, self.agency, self.startDate,
                                          self.endDate, self.sourceType, self.sequenceNumber,
                                          self.stateId],
                    'GetGSDataByHandler':[self.state, self.agency, self.startDate,
                                          self.endDate, self.sourceType, self.sequenceNumber,
                                          self.stateId],
                    'GetCurrentHandlerById':[self.state, self.agency, self.startDate,
                                             self.endDate, self.sourceType, self.sequenceNumber,
                                             self.stateId],
                    'GetHDMaxSequence':[self.state, self.agency, self.startDate, 
                                        self.endDate, self.sequenceNumber],
                    'GetHDDataByFedFac':[self.state, self.agency, self.changeDate, 
                                         self.sourceType, self.sequenceNumber,
                                         self.stateId],
                    'GetPMDataByHandler':[self.state, self.agency, self.startDate,
                                          self.endDate, self.sourceType, self.sequenceNumber,
                                          self.stateId]
        }

        extraneous_values = dict[self.query_type]
        flag = not all(x == '' for x in extraneous_values)
        return flag

    def generate_url(self):
        '''
        Desc: create str represnting url from the initalized value of the ApiUrl
        '''
        url_dict = {'https://rcrainfo.epa.gov/webservices/rcrainfo/public/query/rcra/':self.query_type,
                    '/handlerId/':self.siteId, '/state/':self.state, '/agency/':self.agency, '/startDate/':self.startDate, '/endDate/':self.endDate, '/changeDate/':self.changeDate,
                    '/sourceType/':self.sourceType, '/sequenceNumber/':self.sequenceNumber, '/stateId/':self.stateId}
        generated_url = ''.join([f"{key}{value}" for key, value in url_dict.items() if value])
        return generated_url
    
    def __repr__(self):
        return self.generate_url()
        
    def get_api_data(self):
        '''
        Desc: Send a GET request using a ApiUrl url and convert the received
        XML to a pandas dataframes
        Return:
            data - Dictionary of Pandas dataframes containing major datatypes in the XML
            {} - empty dict that return in case of errors
        '''
        try:
            response = requests.get(self.generate_url()) # request api data from the generated url
            if response.status_code == 200: # if request suceeded process the data
                xml_data = response.text

                tree = ET.fromstring(xml_data)

                _, data = ApiUrl._traverse(tree, ApiUrl._get_categories(self.query_type), self.siteId)

                return data, ApiUrl._confirm_contents(tree, self._get_categories(self.query_type))
        
            else:
                print(F"Failed to fetch data from API. Status code: {response.status_code}")
                return{}
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
        return {}

    @staticmethod
    def _clean(name):
        '''
        Desc: Clean up tag names
        Parameters:
            name - str representing tag name
        Return:
            name.tag.split('}')[-1] - str of cleaned tag name
        '''
        return name.tag.split('}')[-1]
    
    @staticmethod
    def _traverse(element, category_dct, epaid, tableid='', parent=''):
        ''' 
        Desc: sort through xml tree add the results to a dictionary
        Parameters:
            element - xml etree object to be traversed over
            category_dct - dictionary with categories to make seperate dicts for
            epaid - site's epaid
            tableid - id for associated tables with a null default value
            parent - name of associated tables with a null default value
        Return:
            local_dict - dict object with information to add to main tables
            result - dict with information from api data
        '''
        
        # create data containers for function
        local_dict = {}
        result = {v:[] for level_list in category_dct.values() for v in level_list}

        if len(element) == 0: # if the elment has no child, add element's text to local dict
            local_dict[ApiUrl._clean(element)] = element.text
        
        else:
            for child in element:
                tag = ApiUrl._clean(child)

                if tag in category_dct['main']: # if tag in main tags 
                    if not result[tag]: 
                        i = 1 # create int object for tableid if main tag not in result
                    else:
                        i += 1 # add to int object if main tag in result
                    node_tree, node_dict = ApiUrl._traverse(child, category_dct, epaid, i, tag) # run traverse function on child
                    clone_dict = local_dict.copy() # copy local dict
                    clone_dict[f'{tag}_id'] = i # create relational id for row
                    clone_dict.update(node_tree) # add child node information to cloned local dict
                    result[tag].append(clone_dict) # add cloned local dict to result
                    for k in node_dict: # add associated dict information to result
                        if node_dict[k]:
                            result[k] += node_dict[k]

                elif tag in category_dct['associated']: # if tag in associated tags
                    new_table_dict = {'EPA_ID':epaid, f'{parent}_id':tableid} # add epa_id and table_id to dict
                    new_table_dict.update(ApiUrl._traverse(child, category_dct, epaid, tableid, parent)[0]) # traverse children of dict and add to new dict
                    result[tag] += [new_table_dict] # add data to result

                else: # if the child element is neither a main or associated tag 
                    node_tree, node_dict = ApiUrl._traverse(child, category_dct, epaid, tableid, parent)
                    for k in node_dict:
                        if node_dict[k]:
                            result[k] += node_dict[k]
                    local_dict.update(node_tree) # run traverse and add the resulting tree to local dict
                
        return local_dict, result 

    @staticmethod
    def _get_categories(key):
        '''
        Desc: Generates precreated dictionary containing names of main data 
        fields in each request type and returns relevant dict
        Return: Dictionary of the specified query type
        '''
        dict = {
                    'GetCADataByHandler':{'main':['CorrectiveActionArea', 'CorrectiveActionAuthority', 'CorrectiveActionEvent'], 
                                            'associated':['CorrectiveActionRelatedEvent']},
                    'GetCEDataByHandler':{'main':['Violation', 'EnforcementAction', 'Evaluation'], 
                                            'associated':['ViolationEnforcement', 'EvaluationViolation']},
                    'GetHDDataByHandler':{'main':['Handler'],
                                            'associated':['NAICSIdentity', 'FacilityOwnerOperator']},
                    'GetFADataByHandler':{'main':['CostEstimate', 'Mechanism'],
                                            'associated':['CostEstimateRelatedMechanism']},
                    'GetGSDataByHandler':{'main':['GeographicInformation'],
                                            'associated':[]},
                    'GetCurrentHandlerById':{'main':['ReportUniv'],
                                            'associated':[]},
                    'GetHDMaxSequence':{'main':['Handler'],
                                            'associated':[]},
                    'GetHDDataByFedFac':'NotYetBuilt',
                    'GetPMDatabyHandler':'NotYetBuilt'
                    }
        return dict[key]
    
    @staticmethod
    def _confirm_contents(tree_root, categories):
        for el in categories['main']:
            if tree_root.find('.//ns:' + el, namespaces={'ns':"http://www.exchangenetwork.net/schema/RCRA/5"}):
                return True
        return False

class AZ_RcraClient:
    '''
    Creates a RcrainfoClient to access RCRA Info emanifest data

    Args:
        api_id (str): RCRAInfo API ID to authorize client
        api_key (str): RCRAInfo API key to authorize client
    
    Return:
        RcrainfoClient object from emanifest module
    '''
    def __init__(self, api_id, api_key):
        rcrainfo = new_client('prod', api_id = api_id, api_key = api_key)
        if not rcrainfo.is_authenticated:
            rcrainfo.authenticate()
        self.client = rcrainfo

    
    def retrieve_mmanifest_data_short(self, mtn):
        '''
        Desc: Gets information from a manifest, and reformats it into a dataframe
        Arguments:
            mtn (str): Manifest Tracking Form
        return:
            df (dataframe): Dataframe with the fields from the manifest:
                Manifest Tracking Number
                Updated Date
                Shipped Date
                Received Date
                Certified Date
                Generator Epa Site Id
                Generator Name
                Certifier First Name
                Certifier Last Name
                Certifier User ID
                TSDF Epa Site ID
                TSDF Name
                Emanifest Status
                Transporter
                Line Number
                EPA Waste Code
                EPA Waste Description
                Quantity
                Unit of Measurement Code
                Unit of Measurement Description
                Federal Waste Codes
                Management Method Code
        '''
        eman_resp = self.client.get_manifest(mtn)
        emanifest_json=eman_resp.json()
        informational_data = ['manifestTrackingNumber', 'updatedDate', 'shippedDate', 'receivedDate', 'certifiedDate',
                            ['generator', 'epaSiteId'], ['generator', 'name'], ['certifiedBy', 'firstName'],
                            ['certifiedBy', 'lastName'], ['certifiedBy','userId'], ['designatedFacility', 'epaSiteId'], 
                            ['designatedFacility', 'name'], 'status']
        df = pd.json_normalize(emanifest_json, record_path='wastes', meta=informational_data, errors='ignore')
        df['transporter'] = [[el['epaSiteId'] for el in emanifest_json['transporters']]]*len(df)
        df['hazardousWaste.federalWasteCodes'] = df['hazardousWaste.federalWasteCodes'].apply(lambda x: [d['code'] for d in x])
        return df

    def get_mmanifests_short(self,site_id,facility_type,date_type,start_date, end_date):
        '''
        Desc: Creates a dataframe with all eManifest data from the user_provided parameters
        Arguments:

        '''
        resp = self.client.search_mtn(reg=True, siteId = site_id, siteType = facility_type, dateType = date_type, startDate = f'{start_date}T00:00:00Z', endDate = f'{end_date}T00:00:00Z')
        df_list = [self.retrieve_mmanifest_data_short(mtn) for mtn in resp.json()]
        df = pd.concat(df_list)
        df = df.drop(['dotHazardous', 'br', 'pcb', 'quantity.containerNumber', 'quantity.containerType.code', 'quantity.containerType.description',
                    'hazardousWaste.tsdfStateWasteCodes', 'hazardousWaste.generatorStateWasteCodes', 'managementMethod.description',
                    'discrepancyResidueInfo.wasteQuantity', 'discrepancyResidueInfo.wasteType', 'discrepancyResidueInfo.residue'], axis=1)
        df = df.reset_index(drop=True)
        if 'pcbInfos' in df.columns:
            df_info = pd.json_normalize(df['pcbInfos'].apply(lambda x: {} if np.all(pd.isna(x)) else x[0]))
            df_info.columns = ['pcbInfos.dateOfRemoval', 'pcbInfos.weight', 'pcbInfos.bulkIdentity', 'pcbInfos.loadType.code']
            df = pd.concat([df.drop(columns='pcbInfos'), df_info], axis=1)
        df = df[df.columns[9:].tolist() + df.columns[0:9].tolist()]
        return df
        
    def retrieve_mtransporter_data(self, mtn):
        '''
        Desc: Gets the transporters from a manifest
        Parameters:
            mtn: str representing manifest tracking number
        return:
            df - pandas dataframe with transporter infrormation
        '''
        eman_resp = self.client.get_manifest(mtn)
        eman_json = eman_resp.json()
        df = pd.json_normalize(eman_json, 'transporters', meta=['manifestTrackingNumber'], errors='ignore')
        return df

    def get_mtransporter(self, siteId, datetype='', site_type='Generator', start_date='', end_date=''):
        '''
        Desc: Gets all the transporters on emanifests given the provided parameters
        Parameters:
            siteId - str representing siteId
            dateType - str representing dateType
                CertifiedDate 
                ReceivedDate 
                ShippedDate
                UpdatedDate
            site_type - str representing site_type
                Generator
                Tsdf
                Transporter
                RejectionInfo_AlternateTsdf
            start_date - str representing start date in yyyy-MM-dd format
            end_date - str representing end date in yyyy-MM-dd format
        '''
        resp = self.client.search_mtn(reg=True, siteId=siteId, siteType=site_type, dateType=datetype, startDate = f'{start_date}T00:00:00Z', endDate = f'{end_date}T00:00:00Z')
        df = pd.concat([self.retrieve_mtransporter_data(mtn) for mtn in resp.json()])
        df = df.drop(['gisPrimary', 'canEsign', 'limitedEsign', 'hasRegisteredEmanifestUser'], axis=1)
        df = df[['manifestTrackingNumber', 'order'] + df.drop(['manifestTrackingNumber', 'order'], axis=1).columns.tolist()]
        return df

    def get_handler_df(self, handler_id : str, details: bool = False) -> pd.DataFrame:
        '''
        Function to retrieve a dataframe of handler source records (and optional details)
        for a specific handler ID
        This endpoint is restricted to regulators

        Args:
            handler_id (str): EPA Site ID number
            detials (bool): True/false to request additional detials, defaults to false
    
        Returns:
            pandas dataframe object containing handler source records (and optional details)
        '''
        response = self.client.get_handler(handler_id, details)
        if details:
            meta = [['handlerSummary', 'handlerId'], ['handlerSummary', 'handlerName'], ['handlerSummary', 'streetNumber'],
            ['handlerSummary', 'address'], ['handlerSummary', 'address2'], ['handlerSummary', 'city'], ['handlerSummary', 'state'],
            ['handlerSummary', 'foreignState'], ['handlerSummary', 'zip'], ['handlerSummary', 'county'], ['handlerSummary', 'country'],
            ['handlerSummary', 'status'], ['handlerSummary', 'otherId'], ['handlerSummary', 'gisPrimary'], ['handlerSummary', 'latitude'],
            ['handlerSummary', 'longitude'], 'sourceSummariesHsmEnabled', 'sourceSummariesLqgSiteClosureEnabled', 'sourceSummariesLqgConsolidationEnabled',
            'sourceSummariesEpisodicGeneratorEnabled', 'handlerReadOnly', 'handlerAllowDelete', ['tribalData', 'indianLand'], 
            ['tribalData', 'tribalCode'], ['tribalData', 'tribalName']]
            return pd.json_normalize(response.json(), 'sourceSummaries', meta, errors='ignore')
        else:
            return pd.json_normalize(response.json(), errors='ignore')

    def get_cme_lookup_df(self, site_type : str, state : str = 'AZ', nrr_flag : bool = True):
        '''
        ADD Create dataframe with all lookups for a specific activity location and agency,
        including staff, focus area and sub-organization.

        Args:
            site_type (str): One-letter code.   B (State Contracter/Grantee),
                                                C (EPA Contractor/Grantee),
                                                E (EPA),
                                                L (Local),
                                                N (Native American),
                                                S (State),
                                                T (State-Initiated Oversight/Observation/Training Actions),
                                                X (EPA-Initiated Oversight/Observation/Training Actions),
                                                J (Joint State),
                                                P (Joint EPA)
            state (str): Two-letter US postal state code. Defaults to AZ
            nrr_flag (boolean): True/False if Non-Financial Record Review. Defaults to True

        Returns:
            three dataframes corresponding to focusAreas, staff, and subOrganization

        '''
        response_cme_lookup = self.client.get_cme_lookup(state, site_type, nrr_flag)
        response_json = response_cme_lookup.json()
        result = {}
        for k, v in response_json.items():
            result[k]  = pd.json_normalize(v, errors='ignore')
        return result

    def get_cme_types_df(self):
        '''
        Retrieve dataframe of all evaluation types.
        
        Returns:
            dataframe object containing CME evaluation types
                id - three character numeric ID
                code - three character letter code
                description - short description of cme type
                active - bool
                usage - usage number
                userId - User code who added cme type
                lastChange - date of last change of cme type
                helpNotes - additonal notes
                activityLocation - activity location (all labeled HQ)
                followUp - Determines whether type is a FollowUp, NonFollowUp or Other
        '''
        response_cme_types = self.client.get_cme_types()
        df = pd.json_normalize(response_cme_types.json(), errors='ignore')
        return df

    def get_state_waste_codes_df(self, state_code : str):
        '''
        Retrieve dataframe of State Waste Codes for a given state (besides Texas)

        Args:
            state_code: (str) Two-letter state code (e.g. CA, MA)
    
        Returns:
            dataframe object with state waste codes
        '''
        response_state = self.client.get_state_waste_codes(state_code)
        return pd.json_normalize(response_state.json(), errors='ignore')

    def get_fed_waste_codes_df(self):
        '''
        Retrieve dataframe of Federal Waste Codes
    
        Returns:
            dataframe object with federal waste codes
                code - alphanumeric code (format: Z###)
                description - short description of waste code
        '''
        response_federal = self.client.get_fed_waste_codes()
        return pd.json_normalize(response_federal.json(), errors='ignore')

    def get_sites_list(self, site_type : str, state_code : str = 'AZ', reg : bool = False):
        '''
        ADD Retrieve all sites of a type within a state

        Args:
            site_type (str): Site type. Case Sensitive
                                Generator
                                Tsdf
                                Transporter
                                Broker
            state_code (str): Two-letter postal state code
            reg (bool): use endpoint for regulators, defaults to False

        Returns:
            List with strings of EPA site IDs
        '''
        response  = self.client.get_sites(state_code, site_type, reg)
        return response.json()

    def get_entry_ports_df(self):
        '''
        Retrieve dataframe of Ports of Entry

        Returns:
            Dataframe of Ports of Entry
                cityPort - name of port city (and specific locations if there are multiple ports in one city)
                state.code - Two-letter postal state code
                state.name - State name
        '''
        return pd.json_normalize(self.client.get_entry_ports().json(), errors='ignore')
    
    def get_waste_min_codes(self):
        '''
        Retrieve dataframe of Waste minimization codes

        Returns:
            Dataframe of Waste Minimization Codes
                code - Single character letter code
                description - brief description of waste minimzation
        '''
        return pd.json_normalize(self.client.get_waste_min_codes().json(), errors='ignore')
    
    def get_man_method_codes_df(self):
        '''
        Retrieve dataframe of Waste Management Method Codes

        Returns:
            Waste Management Method Codes Dataframe
                code - four letter alphanumeric code (H###)
                description - short description of management method code
        '''
        return pd.json_normalize(self.client.get_man_method_codes().json(), errors='ignore')
    
    def get_source_codes_df(self):
        '''
        Retrieve dataframe of hazardous waste sources

        Returns:
            Hazardous waste source dataframe
                code - three character alphanumeric code (G##)
                description - short description of waste source
        '''
        return pd.json_normalize(self.client.get_source_codes().json(), errors='ignore')
    
    def get_form_codes_df(self):
        '''
        Retrieve form codes dataframe

        Returns:
            Form Codes dataframe
                code - four character alphanumeric code (W###)
                description - short description of form code
        '''
        return pd.json_normalize(self.client.get_form_codes().json(), errors='ignore')
    
    def get_density_uom_df(self):
        '''
        Retrieve dataframe of Density Unit of Measure 

        Returns:
            Density Unit of Measure dataframe
                code - numeric code of density
                description - description of unit of density measurement
        '''
        return pd.json_normalize(self.client.get_density_uom().json(), errors='ignore')
    
    def get_id_numbers_list(self):
        '''
        Retrieves list of Id number

        Returns:
            List of six letter alphanumeric id numers (UN####)
        '''
        return self.client.get_id_numbers().json()
    
    def get_shipping_names_list(self):
        '''
        Retrieves list of shipping names

        Returns:
            list of shipping item names
        '''
        return self.client.get_shipping_names().json()
    
    def get_quantity_uom_df(self):
        '''
        Retrieves a dataframe of the quantity units of measurement

        Returns:
            Quantity Unit of Measurement Dataframe
                code - one letter code
                description - Unit of Measure Quantity 
        '''
        return pd.json_normalize(self.client.get_quantity_uom().json(), errors='ignore')
    
    def get_container_types(self):
        '''
        Retrieves a dataframe of container types

        Returns:
            Container Types Dataframe
                code - two letter code
                description - Container Type 
        '''
        return pd.json_normalize(self.client.get_container_types().json(), errors='ignore')
    
    def get_site_details(self, handler_id : str):
        return pd.json_normalize(self.client.get_site(handler_id).json())
    
    def get_hazard_classes(self):
        return pd.DataFrame(self.client.get_hazard_classes().json())
    
    def get_packing_groups(self):
        return pd.DataFrame(self.client.get_packing_groups().json())
    
    def get_billing_history(self, billingAccount='', billStatus='', startDate='', endDate='', amountChanged='', pageNumber=''):
        '''
        UNTESTED
        '''
        map = {'billingAccount':billingAccount, 'billStatus':billStatus, 'startDate':startDate,
               'endDate':endDate, 'amountChanged':amountChanged, 'pageNumber':pageNumber}
        return pd.json_normalize(self.client.get_billing_history(**map).json(), errors='ignore')
