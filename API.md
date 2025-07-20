
### Server to client messages

| `request`           | Meaning                                                   |
|---------------------|-----------------------------------------------------------|
| `init`              | Initialise, provides basic server metadata                |
| `shutdown`          | Server is shutting down                                   |
| `state`             | Provides the current board state [^1]                     |
| `result`            | Provides the final result of the game                     |
| `action_type`       | Which action to do (`buy` or `execute`)                   |
| `discard_for_exec`  | Which card to discard (when running `execute` action)     |
| `buy_card`          | Which card to buy                                         |
| `card_payment`      | The resources used to pay for the card                    |
| `color_exec`        | The color to execute (`n` times)                          |
| `color_excl`        | The color to not execute                                  |
| `color_foreach`     | An effect is to be executed for each card of which color? |
| `card_from_discard` | Which card to pick up from a discard pile                 |
| `card_exec`         | Which card to execute                                     |
| `spend_resources`   | The resources to spend (when converting)                  |
| `card_move`         | The card to move                                          |
| `where_move_card`   | Where to move the card                                    |

For more info, see the implementation...

[^1] The state is also included in all messages below this one
