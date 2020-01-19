# CarBazaar

## Inspiration
Modern car shopping is fairly dull. All you know about a car is the make, model, year, general condition, and its estimated price; buyers know nothing about the car's life. How did the owner treat their vehicle? What is the history behind this car? How bad was the accident? These are all questions car shoppers ponder. In addition, the answers to these questions potentially influence a customer's decision when purchasing a vehicle. So, we created **Car Bazaar** in order to revolutionize the online car shopping experience.
## What it does
**Car Bazaar** is a car-shopping tool that is centered around the story behind a car. On top of the features on sites like Kelly Blue Book, car shoppers get a more personalized experience with features such as a user's garage and the custom marketplace. Every user who registers on **Car Bazaar** has the option of adding the cars they own to their virtual garage and can add media and stories about their cars. Once a car is added to your garage, you can post it to the marketplace or just leave it for display. In the marketplace, all cars can be searched based on their make, model, and year. **Car Bazaar** will be able to provide a secure opportunity for selling and purchasing cars.
## How we built it
**Car Bazaar** was built using Google Cloud Platform (`Firebase`), `Flask`, `Git`, `HTML/CSS`, and `Python`.
## Challenges we ran into
We struggled with setting up credentials for Firebase Storage and syncing the images stored in Firebase to the car's profile on our website. This was resolved by re-evaluating the urls for the buckets that we were passing in, as well as re-evaluating the rules for the database.
## What we learned
We learned a lot about integrating Firebase' databases with flask-based websites, using Python. We also learned about user authentication, also using Firebase, and storing and retrieving user-specific data.
## The big picture
There are millions of people in the world that value cars as more than just a tool. Whether the car is a hypercar, daily driver, or a classic, consumers can appreciate a car's backstory. Imagine you have to pick between a 2015 Honda Civic EX that has very minimal information or the same car but with a picture of it at the Grand Canyon, interesting stories, and more background information. You would definitely pick the car with more information about it. Even if a person views a car as a tool, they can rest assured that the previous owner took care of their vehicle. 
