# Code For COFFEE

The code and data from this repository can be used to analyze the core components of COFFEE, but due to the high computational requirements of the COFFEE framework, it is usually not possible to solve on laptops and requires the use of servers.

## Code Introduction

This repository mainly stores the implementation code of the COFFEE framework. The first layer contains two folders, *code* and *data*. The *code* folder stores the required code, while the *data* folder stores the required data. The *code* folder includes a *jupytercode* folder, which contains all the *ipynb* files that implement the framework. By reading the *ipynb* file, we can understand the implementation logic of various parts of the COFFEE framework. There are still many Python packages in the *code* folder, which are called in the *ipynb* file. That is to say, the implementation logic is reflected in the *ipynb* file, while the specific implementation details are included in each Python package.

## Data Introduction

The *data* folder contains the data required for each part, which includes both raw data and data generated during implementation processes. Among them, the *OD_425_10_percent.csv* contained in the *ODFile* folder, the *speed_0425.csv* contained in the *speedfile* folder, the *15minCitycv.xls* contained in the *China_IBTDM_effect* folder, the *survey_data.xlsx* file contained in the *survey_data* folder, the *veh_regu_cluster.csv* contained in the *travel_regu_data.csv* folder, and the *veh_all_sam_portrait.csv* file contained in the *veh_portait* folder are the raw data. Except for the aforementioned raw data, all other data are generated during the COFFEE implementation process. Next, we will explain the various raw data:

1. *OD_425_10_percent.csv*: A file composed of data on a certain day of trips in a certain city, in basic units of a trip. Due to the large amount of data in the entire city and to protect data privacy, we randomly sampled 10% of the city's trip data, resulting in a road network load of approximately 10% of the true road network load of the city.
2. *speed_0425.csv* : The average speed of each time slot in the city.
3. *15minCitycv.xls*: A file on the composition of the imbalance of travel demand in various cities in China.
4. *survey_data.xlsx*: Distribute questionnaires to travelers to investigate their acceptance of COFFEE.
5. *veh_regu_cluster.csv*: Based on the paper "Understanding vehicles commuting pattern based on license plate recognition data", conduct a vehicle portrait and divide the road network vehicles into different categories.
6. *travel_regu_data.csv*: The regularity of vehicle travel in the road network.

## Environment Configuration

Environment Requirements: Python 3.7

Package Requirements: Please refer to requirements.txt

It should be noted that with the sample data in this repository, all code can be executed on a personal computer, while the complete data requires processing on a server with more than 128GB of memory.

## Steps for Code Implementation

### 1. Evaluation of  Traffic Demand Management

First, we need to evaluate the effectiveness of the traffic demand management strategies, specifically the TDM evaluation model mentioned in the manuscript. The implementation and results of this algorithm are presented in the file "MFD and Evaluation of Traffic Demand Management.ipynb." As described in the data, we conducted a random sampling of 10% of the OD data; therefore, the road network load in the TDM evaluation model is only about 1/10 of the true data. Although a 10% random sample was taken, the distribution of the road network load is indeed the same as the overall data, and the performance and results of the algorithm can accurately reflect the overall outcomes. The traffic state simulation results obtained in Hangzhou are shown in the figure below (the road network load is only about 1/10 of the true load, and the average speed of the road network is based on the actual data):

![Traffic State Simulation Results for Hangzhou](https://github.com/user-attachments/assets/3246fc11-0a68-467a-ae09-c1cf1efbb07a)


### 2. Divide the sample set into sub sample sets of the same distribution

Directly using the COFFEE framework to perform peak-shifting on all data cannot be achieved even on a server due to the excessive number of optimization variables. Therefore, it is necessary to divide the sample set into sub-sample sets with the same distribution. This step is implemented in the file "Divide the sample set into sub sample sets of the same distribution.ipynb." The results of the division are shown in the figure below:

![dataset split results](https://github.com/user-attachments/assets/b4c20f9b-d08d-4a05-8957-ca53875b15dc)


### 3. Analysis of acceptance of COFFEE and analysis of its effectiveness based on acceptance

First, based on the survey data, we analyze the willingness of travelers of different travel behavior to adjust their departure times. Then, using the obtained willingness to adjust departure times, we derive the distribution of willingness for all trips, ensuring that this distribution matches that obtained from the survey. On this basis, we can utilize the COFFEE framework to perform peak-shifting for trips. Since this is only for demonstration purposes, we randomly sampled 2000 trips from each sub-sample set during the execution of the mixed-integer linear programming model to facilitate optimization; otherwise, it would be difficult to execute successfully on a personal computer. The results of the optimization are shown in the figure below (it is important to emphasize that two sampling steps were conducted: the first sampling involved a 10% random sample of the entire dataset, and the second sampling involved selecting 2000 trips from each optimization subset). The figure below has not undergone the TDM evaluation model. In the ipynb file, we provide the code; however, it does not generate results similar to those in the manuscript. This is because the TDM evaluation model was only subjected to a single sampling, while the optimization model involved two rounds of sampling. Therefore, the results obtained cannot match each other. If both were to match, we could achieve results similar to those in the manuscript.

![COFFEE effect](https://github.com/user-attachments/assets/40d9a9cb-edbe-483a-904a-f94074c8969b)


### 4. Analysis  of  Travel Time Changes  in  Seven  Cities

The analysis of changes in travel times for travelers in the seven cities after implementing COFFEE can be found in the document titled "Analysis of Travel Times in Seven Cities.ipynb." Since the analysis here is based on sampling, the conclusions may differ from those in the manuscript. Therefore, please refer primarily to the analytical approach presented in the code.

### 5. Analysis of congestion relief effects under three strategies: travel restriction policies, congestion pricing policies, and random time-shifting

The analysis focuses on travel restriction policies, congestion pricing policies, and random time-shifting strategies, simulating the congestion relief benefits under each of these three strategies. This analysis can be found in the documents titled Analysis of multi city travel restriction policies.ipynb, Comparison of SS in seven cities.ipynb, and Comparison of the Effectiveness of Congestion Charging Policies in Seven Cities.ipynb. In the above analysis, the road network load was sampled at 10%, but its distribution is consistent with the overall distribution.

### 6. Analysis of Factors Influencing COFFEE effect

An analysis of the factors influencing the COFFEE effect can be found in the document titled "Analysis of Factors Influencing COFFEE Effect.ipynb."

