# Poker analysis
My goal is to create a poker engine to calculate the likelyhood of me winning 
poker hands. In particular, I want to use this tool to learn more optimal way 
of playing poker by analising the board better.

## Ideas on how to make the engine
My first solution was to simply go through every possible combination of hands,
evaluate them and count how many times we win. As of time of writing this is 
already implemented in main branch. However, this solution is extremely limited 
and wastefull. I want to build something more real-time (current solution on
main runs for around a second in cython implementation)

I also want to add more functionality. First implementation is only returning
the % number of games we win. It would be much better to see what kind of hands 
beat us and with what probability. Finally, my current implementation does not 
allow the exclusion of cards that are shown during game. Sometimes we gain
information on cards that are thrown away by other players. It would be ideal
to be able to exclude those cards from our calculations.

Therefore going forward I addopt new strategy:
1. I will look at my cards and calculate all hands that I can have.
2. After I find it, I will find all enemy hands that beat my hands.
3. calculate the probability of each
4. display information to the user
5. profit

## Naming convention
In first attempt I notised unnecessary mental overhead with naming variables.
Going forward I will use:
- `whole_cards`: cards that I have in my hand
- `community_cards`: cards on the table available to everyone
- `card_rank`: card "name" so an ace or a king or a duce
- `card_suite`: card "color" so clubs (♣), diamonds (♦), hearts (♥) and spades (♠)
