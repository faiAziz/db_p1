PostgreSQL account: sls2305

URL: https://35.211.67.64:8111/

Description:
In this project we created a database from the Department of Health New York City Restaurant Inspection Results, which includes information and inspection results from NYC restaurants. We successfully implemented all parts of the original proposal from Part 1. This includes allowing users to search for restaurants filtering by distance, health inspection grade, and type of cuisine. Users can also view the inspection violation notes of a restaurant. We also allow users to select multiple types of cuisine, or multiple inspection grades in a single query which was not explicitly mentioned in the original proposal. We added two new features, the first allowing the user to find all restaurants in a given borough. The second new feature allows users to select all restaurants North or South of a given latitude. Our features successfully demonstrate the full functionality of the database through a variety of user inputs.

Interesting page 1: cuisine search feature

The first page that we thought was most interesting was the cuisine search feature. This allows a user to check boxes of the type of cuisine they would like to find, and returns a list of restaurants and their address that serve those foods. This is very practical for users to find a place to eat depending on what they are in the mood for. An example query for this function is shown below, which involves a natural join between restaurant and address.
'SELECT R.name, A.building, A.street, A.zip 
FROM restaurant R, address A 
WHERE R.camis = A.camis AND R.cuisine IN ('Hamburgers', 'Donuts');

Interesting page 2: distance search feature

The second page that we thought was most interesting was the distance search feature. This first requires a user to allow sharing of their current location. Then the user can use the slider to select a distance between 0 and 20km. When the user clicks submit, a list of restaurants is returned within the selected distance. The steps of how we accomplish this are as follows: First, the slider ranges from 0-100. We multiply the value by 200 to convert to a selection of 0-20,000 meters. In the query, we compute the distance from the current user location to all other restaurants, and return the restaurants which are within the selected radius. The distance is calculated using the pythagorean theorem, which is multiplied by a constant value to convert from degrees latitude/longitude to meters. An example query is shown below:
SELECT R.name, R.cuisine from restaurant R, address A 
WHERE R.camis = A.camis AND ' + str(radius) + '> ( sqrt(((' + str(lat) + ' - A.latitude)* (' + str(lat) + ' - A.latitude)) + ((' + str(long) + ' - A.longitude)*(' + str(long) + ' - A.longitude)))* 111139)
 
