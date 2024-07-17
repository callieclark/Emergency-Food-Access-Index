# **Emergency-Food-Access-Index**

Source code and data repository for "A multi-dimensional access index: Exploring emergency food assistance in New York City" (insert link here when paper is out). Our paper proposes an open-source, reproducible framework to evaluate emergency food access. We provide the code and data with the goal of others being able to apply the provided framework to different geographies and domains. The repo contains the anonymized NYC food pantry data and the simulated travel time data, as well as all the code used to simulate and construct our proposed Emergency Food Access Index. 

### Project Team

- Callie Clark (crc9978@nyu.edu)
- Christa Perfit
- Alice Reznickvoa, PhD

__

More than one in ten New Yorkers are food insecure and fifty percent live below the self-sufficiency standard, a significant increase from thirty-six percent in 2021. Free food, or emergency food assistance, fills an important role in supporting often insufficient and unreliable government benefits. However, research shows that food pantries that provide free food to their communities are often inaccessible -- both geographically, due to distance coupled with limited transit options, and because of limited open hours that do not align with clients’ schedules. However, access is often defined and measured in terms of distance only. We propose an access index that employs a multi-dimensional approach including geography, operating hours, and availability of transit infrastructure. We produce a novel dataset by simulating travel time from each census tract to the nearest open food pantry across New York City for 28 time periods and four modes of transportation. Our simulation employs the OSMnx Python package that overlays network analysis capabilities on OpenStreetMap data to simulate walking, biking and driving travel times, and we implement the Urban Access python package to simulate public transit travel times. We incorporate 2023 data on food pantry location and operating hours. Combining all aspects, we propose an index that quantifies spatiotemporal access by mode and we further contrast it with need based on food insecurity data. This study expands on the traditional view of food access by including temporal data and modes of transportation thus informing discourse about food justice.  Our study focuses on emergency food programs, but it is a stepping stone towards a holistic, data-centered view of overall food access.

___

Please cite the following, if using the data in published work:
[insert citation]
