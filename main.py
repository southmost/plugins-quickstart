import json
import random

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

FACTS = [
    "Texas is known as the Lone Star State because of the single star on its flag, representing its former status as an independent republic.",
    "The state motto of Texas is 'Friendship,' which reflects the warm and welcoming nature of its people.",
    "The Texas State Capitol in Austin is taller than the U.S. Capitol in Washington, D.C. It is also the largest state capitol building in terms of square footage.",
    "Texas is home to the world's largest rodeo, the Houston Livestock Show and Rodeo. It attracts millions of visitors each year.",
    "The famous Alamo Mission, located in San Antonio, played a significant role in the Texas Revolution. It is now a popular tourist attraction.",
    "Texas is known for its delicious barbecue. The state takes pride in its various styles of barbecue, including Central Texas, East Texas, and South Texas.",
    "Texas is home to the largest bat colony in North America. The Congress Avenue Bridge in Austin is home to over 1.5 million bats.",
    "The Lyndon B. Johnson Space Center, located in Houston, is the training center for NASA astronauts.",
    "Texas is the leading crude oil producer in the United States and has a rich history in the oil industry.",
    "The King Ranch in South Texas is one of the largest ranches in the world. It spans over 825,000 acres, which is larger than the state of Rhode Island.",
    "The city of Amarillo, Texas, is home to the Cadillac Ranch, an art installation featuring ten Cadillacs buried nose-first in the ground.",
    "The San Antonio River Walk is a famous tourist attraction featuring a network of walkways along the San Antonio River.",
    "Texas is home to the world's largest urban bat colony, located under the Congress Avenue Bridge in Austin.",
    "The official state dish of Texas is chili, and Texans take their chili seriously.",
    "The San Antonio Spurs, a professional basketball team, have won multiple NBA championships.",
    "Texas has a rich musical heritage and has produced legendary musicians like Willie Nelson, Buddy Holly, and Beyoncé.",
    "The Big Bend National Park in Texas is home to stunning landscapes and diverse wildlife.",
    "Texas is known for its vast open spaces, with wide-ranging deserts, prairies, and coastal areas.",
    "The Texas State Fair held in Dallas is one of the largest and most renowned state fairs in the United States.",
    "The NASA's Mission Control Center, responsible for managing human spaceflight missions, is located in Houston.",
    "Texas is home to numerous top-tier universities, including the University of Texas at Austin and Texas A&M University.",
    "The Guadalupe Mountains in Texas contain the highest point in the state, reaching an elevation of 8,751 feet (2,667 meters).",
    "The city of Austin, Texas, is often referred to as the 'Live Music Capital of the World' due to its vibrant music scene.",
    "The Dallas/Fort Worth International Airport is one of the busiest airports in the world, connecting Texas to various destinations worldwide.",
    "The Texas bluebonnet is the state flower of Texas and is known for its vibrant blue color.",
    "Texas has a diverse cultural heritage influenced by Native American, Mexican, and Western traditions.",
    "The annual South by Southwest (SXSW) festival held in Austin showcases music, film, and interactive media.",
    "Texas has a variety of unique geographical features, including the Palo Duro Canyon, the second-largest canyon in the United States.",
    "The world's largest bathtub race takes place in the Texas city of Marble Falls every year.",
    "Texas is home to the largest wind power capacity in the United States, harnessing its vast wind resources.",
    "The Texas Medical Center in Houston is the largest medical complex in the world.",
    "Texas has a wide range of wildlife, including white-tailed deer, armadillos, bobcats, and various bird species.",
    "The State Fair of Texas held in Dallas is known for its iconic deep-fried foods, including deep-fried butter and deep-fried Oreos.",
    "The Texas Rangers, one of the oldest law enforcement agencies in North America, have a rich history of maintaining peace and order in the state.",
    "The city of Galveston, Texas, is home to one of the largest collections of Victorian architecture in the United States.",
    "The Texas Hill Country is known for its picturesque landscapes, vineyards, and charming small towns.",
    "The Texas Longhorn is the official state large mammal of Texas, known for its iconic long horns and historical significance.",
    "Texas has a vibrant sports culture, with passionate fans supporting teams like the Dallas Cowboys, Houston Texans, and San Antonio Spurs.",
    "The Texas State Library and Archives Commission houses extensive historical records and documents that preserve the state's history.",
    "Texas has a rich history in the cattle industry, with sprawling ranches and iconic cattle drives.",
    "The world's first domed stadium, the Astrodome, was built in Houston, Texas, and was once called the 'Eighth Wonder of the World.'",
    "Texas is home to the Guadalupe Peak, the highest natural point in Texas, offering breathtaking views from its summit.",
    "The city of El Paso, located in the westernmost corner of Texas, is closer to the capital cities of three other states (New Mexico, Arizona, and Mexico) than to the Texas capital, Austin.",
    "The Houston Museum of Natural Science is one of the most visited museums in the United States, featuring exhibits on dinosaurs, gems, and space exploration.",
    "Texas has a significant presence in the film industry, with cities like Austin, Houston, and Dallas serving as popular filming locations for movies and TV shows.",
    "The Texas State Railroad offers scenic train rides through the piney woods of East Texas, providing a nostalgic experience of bygone eras.",
    "Texas is home to numerous natural springs, including the famous Barton Springs in Austin, which maintains a constant temperature of around 68 degrees Fahrenheit (20 degrees Celsius).",
    "The San Antonio Spurs, a professional basketball team based in San Antonio, has won multiple NBA championships.",
    "Texas is known for its love of high school football, with legendary Friday night games drawing passionate crowds across the state.",
    "The Texas State Aquarium, located in Corpus Christi, showcases marine life from the Gulf of Mexico and other coastal regions.",
    "Texas has a diverse culinary scene, influenced by various cultures, offering mouthwatering dishes like Tex-Mex, kolaches, and Texas-style barbecue.",
    "The Enchanted Rock State Natural Area in Texas is a massive pink granite dome that attracts rock climbers and nature enthusiasts.",
    "The George W. Bush Presidential Center, located in Dallas, is a museum and library dedicated to the 43rd President of the United States.",
    "Texas has a rich heritage in the cowboy and Western lifestyle, with rodeos, cattle ranches, and Western-themed events throughout the state.",
    "The Texas Hill Country is known for its picturesque wineries and vineyards, offering wine enthusiasts a delightful experience.",
    "The state reptile of Texas is the Texas horned lizard, also known as the horny toad, famous for its unique appearance and ability to shoot blood from its eyes as a defense mechanism.",
    "Texas is home to the world's largest urban bat colony, located under the Congress Avenue Bridge in Austin, with over 1.5 million bats.",
    "The Texas State Fair held in Dallas is famous for its iconic fried food creations, including fried cookie dough, fried bacon cinnamon rolls, and fried bubblegum.",
    "The Texas Renaissance Festival, held near Plantersville, is one of the largest and most acclaimed Renaissance fairs in the United States.",
    "Texas is known for its vast and diverse landscapes, including the rugged canyons of Palo Duro, the sandy beaches of South Padre Island, and the majestic mountains of Big Bend.",
    "The city of Fort Worth, Texas, is home to the world's first and largest indoor rodeo, known as the Fort Worth Stock Show & Rodeo.",
    "Texas has a vibrant music scene, with influential genres like country, blues, and Western swing having deep roots in the state's culture.",
    "The Texas State Railroad, operating historic steam and diesel locomotives, offers scenic train rides through the piney woods of East Texas.",
    "The Caverns of Sonora, located in West Texas, is a world-renowned cave system known for its stunning formations and natural beauty.",
    "The city of Corpus Christi, Texas, is home to the USS Lexington, an aircraft carrier turned museum that offers a glimpse into naval history.",
    "Texas is home to numerous natural springs, including the famous Jacob's Well in Wimberley, known for its crystal-clear waters and underwater caves.",
    "The Dr. Pepper Museum, located in Waco, Texas, celebrates the iconic soft drink's history and features interactive exhibits for visitors to enjoy.",
    "Texas has a rich cowboy heritage, with rodeos, cattle drives, and Western-style events preserving the state's cowboy culture.",
    "The city of San Antonio, Texas, is famous for its vibrant River Walk, a scenic pedestrian promenade lined with shops, restaurants, and beautiful architecture.",
    "The Laredo International Bridge in Texas is one of the busiest border crossings in the United States, connecting Laredo to Nuevo Laredo in Mexico.",
    "Texas has a wide range of outdoor recreational activities, including fishing, hunting, hiking, and boating, thanks to its diverse landscapes and abundant wildlife.",
    "The Houston Livestock Show and Rodeo, held annually, is the largest livestock exhibition and rodeo in the world, attracting millions of visitors.",
    "Texas is home to numerous state parks, offering opportunities for camping, hiking, and wildlife observation, such as Garner State Park and Palo Duro Canyon State Park.",
    "The city of Dallas, Texas, is home to the Dallas Cowboys, one of the most valuable sports franchises in the world.",
    "Texas has a thriving arts and culture scene, with world-class museums, theaters, and galleries in cities like Houston, Dallas, and Austin.",
    "The Texas State Aquarium in Corpus Christi showcases a wide variety of marine life from the Gulf of Mexico, providing educational and interactive experiences for visitors.",
    "Texas has a rich literary history, producing renowned authors like Cormac McCarthy, Sandra Cisneros, and Larry McMurtry.",
    "The city of Galveston, Texas, is known for its historic architecture, beautiful beaches, and popular attractions like Moody Gardens and Schlitterbahn Waterpark.",
    "Texas has a strong tradition of country music, with influential musicians such as George Strait, Willie Nelson, and Johnny Cash hailing from the state.",
    "The Texas A&M University in College Station is one of the largest universities in the United States and has a storied history in academics and sports."
]

@app.get("/fact")
async def get_fact():
    # Generate a random fact
    fact = random.choice(FACTS)
    return quart.Response(response=json.dumps({
        "fact": fact
    }),
                        status=200)

@app.post("/todos/<string:username>")
async def add_todo(username):
  request = await quart.request.get_json(force=True)
  if username not in _TODOS:
    _TODOS[username] = []
  _TODOS[username].append(request["todo"])
  return quart.Response(response='OK', status=200)


@app.get("/todos/<string:username>")
async def get_todos(username):
  facts = [
    "Texas was once an independent nation.",
    "The King Ranch in Texas is bigger than the state of Rhode Island.",
    "Dallas/Fort Worth International Airport is larger than Manhattan.",
    "The first domed stadium in the U.S. was the Astrodome in Houston.",
    "The deadliest natural disaster in U.S. history was the 1900 hurricane in Galveston, which killed between 8,000-12,000 people."
  ]
  return quart.Response(response=json.dumps({
    "username": username,
    "facts": facts
  }),
                        status=200)


@app.delete("/todos/<string:username>")
async def delete_todo(username):
  request = await quart.request.get_json(force=True)
  todo_idx = request["todo_idx"]
  # fail silently, it's a simple plugin
  if 0 <= todo_idx < len(_TODOS[username]):
    _TODOS[username].pop(todo_idx)
  return quart.Response(response='OK', status=200)


@app.get("/logo.png")
async def plugin_logo():
  filename = 'logo.png'
  return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
  host = request.headers['Host']
  with open("./.well-known/ai-plugin.json") as f:
    text = f.read()
    return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
  host = request.headers['Host']
  with open("openapi.yaml") as f:
    text = f.read()
    return quart.Response(text, mimetype="text/yaml")


def main():
  app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
  main()
