# Industrial IoT for Digitization of Electronic Assets - Final Project

<p style="margin-top: 100px; margin-bottom: 20px;"></p>

<p align="center">
<img src="../Module 0/imgs/dtu_logo.png" width="100"/>
</p>
<p align="center">
 <b>
Technical University of Denmark <br />
Wind and Energy Systems<b> <br />
</p>

**Project Title:** System Identification of the Wastewater Pump Station.

**Deadline:** 19th of January, 2024

This project aims to explore and analyze the wastewater pump station through a system identification approach. The primary goal is to understand the operational dynamics of the station and evaluate various strategies to enhance its performance. Students will be divided into three groups, with each group focusing on the same main project but focusing on different analysis and control strategies.

## Common Objectives:

Each group will work on basic system identification of the wastewater pump station. This will involve building the static or dynamic model, understanding the basics of system behavior, using the digital twin to forecast future scenarios.
The dataset can be downloaded from the data folder in this repository.

## Group Objectives:
### Track A:

This project focuses on the analysis of the station and the development of a control strategy using MPC. You will be free to use one of the following objectives:

- **Reducing CO2 emissions.**
  *Objective*: Reduce the overall CO₂ emission of the wastewater station ensuring the proper operational conditions.
- **Increase the overall Energy Efficiency of the station**
  *Objective*: Design a real-time controller that minimizes the overall energy consumption of the wastewater pump station.



### Track B:

This track will focus on building a digital twin of the wastewater, focusing on the following points.


- Start by building the static models of all the features of the station *(inflow, outflow, speed vs. power, and speed vs outflow)*. Then, increase the complexity of the model considering the dynamics of the station using ARX and the implementation of AI for system identification.
- Perform an in-depth data analysis of the data with visualization. Clean the data and remove outliers, if needed.
- Divide the dataset into train and test and analyze and compare the performance of all models using the tools and techniques learned in the course.
- Evaluate the performance of the Digital Twin over different time horizons. How does the model perform in the short term? How does the model perform in the long term?
- Enhance your findings with residual analysis and hypothesis testing.
- Pick your best model across the pump station features, forecast a few seconds/minutes forward in the future, and run the model on the cloud showing the results in Grafana.

# Evaluation Criteria:
Each group will have 20 minutes to present their project and each member is asked to actively participate in the presentation. Consider also showing parts of code during the presentation. 

- Create a public repository on GitHub and share the link with the TAs.
- Code Implementations, Plots, and Graphs
- Quality and accuracy of system identification analysis.
- Effectiveness of the proposed control strategy based on the chosen objective function.
- Clarity and creativity of the presentation.


If you have any question about the code,<ins>open an issue here</ins>  or email us at: 
<p align="left">
 <br />
 <b>Alessandro Quattrociocchi (<a href="mailto:alqua@dtu.dk">alqua@dtu.dk</a>)
<br />
 <b>Jakob Schneider (<a href="mailto:jaksne@dtu.dk">jaksne@dtu.dk</a>)
<br />
</p>