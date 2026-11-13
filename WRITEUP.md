## 1. Scores
- Baseline (given): 1471712.0
- My solver: 2225449.0

This is roughly 51% better than the baseline score

## 2. Five strategies I tried
1. I checked the demand of each food item by day of the week instead of just calculating the mean and noticed things like burgers have more demand on weekends than weekdays.
2. Next I looked at the different features and worked out the correlation between them and the food items' demand. For example, it showed me that tea is drank more on exam days and that sandwiches have a drop when the competitor has a discount.
3. Then I trained a prediction model (RandomForest) for each of the 5 items, using all 11 features together instead of looking at them independantly.
4. I added an adjustment of 'waste against running out' instead of the just preparing what was predicted as I noticed that certain items were more cheap to waste (like tea), and others were expensive to waste (like burgers). For this, I prepared more items that were cheap to waste and made less expensive to waste items.
5. A capacity awareness step was introduced as the instructions stated that there is a 500 minute kitchen limit before receiving the penalties.

## 3. Three strategies that failed
1. Obviously preparing the average demand/baseline was using way more than 500 minutes of the kitchen time which would mean there would be a lot of penalization.
2. I expected that leftover from the previous day woukd be an important feature but it had close to 0 correlation with demand for all 5 items.
3. Even after figuring out the balance for waste and stockout, it was still a lot over the 500 minute budget which is why I then introduced the capacity awareness step.

## 4. Why my final solution is not simply predicting demand
The final solution I came up with was not just predicting demand as that would ignore the costs of wasting items and running out of items. I had to decide how much to actually cook with that in mind as well as also ensuring that I was not going too over the 500 minute limit as that would also had cost due to the penalty. For those reasons, I had to decide what items would be worth using up most of that time. Two items can have the same predicted dmeand but have very different amounts actually prepared as a result of the factors mentioned above.

## 5. Features or rules I discovered
- Tea was more in demand on rainy and exam days, and less on hot days
- Poha was more with high footfall on weekdays
- Sandwich was hurt by discounts at competitors
- Juice was more in demand on hot days and less on rainy days
- Burger was more one weekends/sport days
- previous_day_leftover_index was not useful

## 6. How I handled kitchen capacity
As the 500 minute limit was not a strict cut off, I let all 5 items 'compete' for the time given; whichever item was more worth to make another unit for, compared to the other items, was made next. The production of an item would stop once its next potential unit is not worth the cost anymore - up to 500 minutes it was free but after that it had to beat the 2.5 point cost per minute. To do this, heapq (a priority queue algorithm) was used as it keeps track of the current best option quickly instead of check all 5 items each round in a loop as that would be slower.