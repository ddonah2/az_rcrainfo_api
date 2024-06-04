# AZ RCRAInfo Access Portal

## Introduction

The AZ RCRAInfo Access Portal provides a portal for a non-technical user to make requests to RCRAInfo public apis and RCRAInfo eManifests functionality. The software is made in python and built off of the EPA's eManifest module, RCRAInfo public access APIs and the tkinter module. Once further EPA access functionalities are created, the project will expand to include those

## Table of Contents
[1. Installation Instructions](#installation-instructions)

[2. Set Up](#api-access-set-up)

[3. Use Guide](#use-guide)

## Installation Instructions

To be written

## API Access Set Up

The EPA Data Request Console uses two EPA services EPA RCRAInfo public APIs, and the EPA eManifest Module. All the information provided by the EPA RCRAInfo APIs are publicly accessible, but the information provided by the eManifest module is not. In order to use any of the eManifest queries, you will need a RCRAInfo API Key and ID. To get access to these you will need a RCRAInfo account with API Access. This can be done by [[a RCRAInfo administrator in your department and requesting access]].

Once you have API access, you will need to log into RCRAInfo, and navigate to the Documentation tab on the blue navigation bar at the top of the screen.



When your mouse hovers over the tools tab, a dropdown menu will appear. Click on the ‘Translation/API Maintenance’ option. 



Once you click on the “Translation/API Maintenance” option, you will be directed to a new page. A second navigation bar will appear below the main navigation bar with the options “Overview”, “Direct Upload”, “Manage API” and “Audit API”. Click on the “Manage API” option. 



If you have already generated a key, this page will look slightly different, but there will be a blue button at the bottom of the following tab saying either “Generate API Key” or “Regenerate API Key”. Click on this button and the API key will be generated. Copy the API Key to a secure location as you will not be able to access it again without regenerating the API Key. The API ID will not change and you will be able to always access it from this tab without regenerating the key. 

The API Key periodically expires, so if you are receiving errors using an API Key, and you know that there is not an issue with the API Key, you may need to repeat this process and regenerate the key. 


## Use Guide

### Request Types
#### GetManifestData
Retrieves eManifest data for a specified EPA ID. Each row corresponds to a different waste line. Fields include manifest tracking number, updated, shipped, received and certified dates, generator and transporter information, and wasteline information.

#### GetCEDataByHandler
Retrieves Compliance, Monitoring and Enforcement data for a specified EPA ID. Response includes 5 tables, Violation, EnforcementAction, Evaluation, ViolationEnforcement, EvaluationViolation. The last two tables are connector tables linking Evaluation, EnforcementAction and Evaluation together. 

#### GetCADataByHandler
Retrieve information on Corrective Action relating to a specified EPA ID. Response includes 4 tables: CorrectiveActionArea, where the corrective action occurred; CorrectiveActionAuthority, who carried out the corrective action; CorrectiveActionEvent, what the corrective action was and CorrectiveActionRelatedEvent.

#### GetFADataByHandler
Retrieves Financial Assurance data for a specified EPA ID. Response includes 3 tables: CostEstimate; Mechanism, containing information on payment delivery and CostEstimateRelatedMechanism. 

#### GetGSDataByHandler
Retrieves Geospatial Data for a specified EPA ID. Response includes geographic coordinates.

#### GetHDDataByHandler
Contains handler report data for a specified EPA ID. Response includes 3 tables: Handler, reports with data on the status, location, management and activity of the site; NAICSIdentity, NAICS codes associated with each report and FacilityOwnerOperator, information on the site owner with each report.

#### GetHDMaxSequence
Contains Handler data for the maximum sequence number for a specified EPA ID. Contains source type code and source record sequence number.

### Entry Field Definitions

#### Request Type
This entry field is a dropdown menu that allows the user to choose which request type they wish to access. Once one of these is selected, the rest of the entry fields needed will be loaded into the user portal.  

#### API ID & API Key
The API ID and API Key are access keys to retrieve eManifest data not immediately publicly accessible. The API ID is a sequence of 5 variable length text segments composed of random characters, with each segment being separated by dashes. The API Key is a short string of random characters, and subject to change. This is a required field. (For more information on accessing these, see the above subsection “API Set Up” within the “Set Up” section)

#### Site ID
This text entry determines which site the query will attempt to access. The accepted format for this field is a twelve-character EPA Hazardous Waste ID (roughly in the format AZ##########). This is a required field

#### Facility Type
The Facility Type field is a drop down used for eManifest queries that determines which facility type the query will look for the Site ID in. The options are “Generator”, “Tsdf”, “Transporter” and “RejectionInfo_AlternateTsdf”. This is a required field.

#### Date Type
The Date Type field is a drop down used for eManifests queries that determines which date type field in eManifests the provided date ranges will filter on. The options are “CertifiedDate”, “ReceivedDate”, “ShippedDate” and “UpdatedDate”. This is a required field.

#### Start Date
The start date field is a text entry in the format of YYYY-MM-DD (ex: 2000-01-13) that determines where the date range for eManifest data will start to collect eManifests. This is a required field.

#### End Date
The end date field is a text entry in the format of YYYY-MM-DD (ex: 2000-01-13) that determines where the date range for eManifest data will stop eManifests. This is a required field.

#### Change Date
The change date field is a text entry in the format of YYYY-MM-DD that determines after which date new entries to the query will be collected. 

#### State/State ID
The state field is a text entry that limits the response to the query to the limits of the provided state. The accepted for this entry is the two letter postal code (ex: AZ). 

#### Source Type
#### Sequence Number
#### Issuing Agency Type
The issuing agency field is a drop down entry that limits the issuing agency for CME violations to the specified agency. 

