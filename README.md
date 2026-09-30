# BugAI-Priority-Prediction-and-Solution-Recommendation-


BugAI is a machine learning based web application developed to analyze software bug descriptions and predict their severity and priority. The system also provides possible solutions for the reported bug using a combination of rule-based recommendations and a locally running AI model.

The main purpose of the project is to help developers and testing teams understand the seriousness of a reported bug and get initial troubleshooting guidance from the same interface.

## Project Overview

In software development, bug reports can have different levels of severity and urgency. Manually identifying the appropriate priority can sometimes be difficult, especially when a bug description is unclear or contains limited information.

BugAI takes a bug description as input and performs the following steps:

1. Cleans and preprocesses the input text.
2. Converts the text into numerical features using TF-IDF.
3. Uses a trained LinearSVC model to predict bug severity.
4. Maps the predicted severity to a priority level.
5. Calculates a confidence score for the prediction.
6. Provides a recommended solution using rule-based logic, AI, or a combination of both.
7. Displays the complete result through a web-based dashboard.

## System Workflow

```text
Bug Description
       |
       v
Text Preprocessing
       |
       v
TF-IDF Vectorization
       |
       v
LinearSVC Model
       |
       v
Severity Prediction
       |
       v
Priority Mapping
       |
       v
Recommendation System
       |
       +------------------+
       |                  |
   Rule-Based           AI-Based
       |                (Mistral)
       |                  |
       +--------+---------+
                |
                v
          Solution Output
                |
                v
            Web Dashboard