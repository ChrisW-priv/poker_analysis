#include <iostream>
#include <tuple>
#include <cstdint>

enum PokerHand {
    HighCard,
    Pair,
    ThreeOfAKind,
    TwoPair,
    Straight,
    FullHouse,
    FourOfAKind,
    ERROR
};

/* const int ACE_ENCODED_LAST = /* Your value here */;
/* const int ACE_ENCODED_ONE = /* Your value here */; 

extern "C" {
    void evaluate7cards(uint8_t* sorted_cards, int* result1, int* result2) {
        // Convert the logic of your Python function to C++
        // ...
        for (int i=0; i<5; ++i){
            std::cout << +sorted_cards[i];
            std::cout << '\n';
        }

        *result1 = 10;
        *result2 = 20;
        return ;
    }
}

