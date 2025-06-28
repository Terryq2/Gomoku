# Gomoku


## Board
For an $n\times n$ board we index the top left corner as $(0,0)$. A larger $x$ coordinate brings us more right relative to the origin. A larger $y$ coordinate brings us more down relative to the origin. This scheme is illustrated on the following $15\times15$ board.

<img src="/images/board.png" width=50% height=50%>

## Heuristics
### Evaluating diagonals
#### A characterization of diagonals
We call a line a diagonal if it has two endpoints $p_1=(x_1,y_1)$ and $p_2 =(x_2,y_2)$ with $x_1 < x_2$ and $y_1< y_2$ or $y_2<y_1$. For convenience, we call a diagonal a left diagonal if $x_1 < x_2$ and $y_1< y_2$ and 
a diagonal a right diagonal if $x_1 < x_2$ and $y_2< y_1$. This is best illustrated by the following diagram, where the blue line is a left diagonal and the red line is a right diagonal.

<img src="/images/diagonals.png" width=56% height=56%>

#### Design
Upon each placement of stones we keep track of which diagonal the stone is placed onto and the number of stones on that diagonal. When evaluating a position, we skip those diagonals which contain no stones. This speeds ups our evaluation function by some constant factor when compared to
an naive implementation that goes through every single possible diagonals. This gain in efficiency decays the longer the game is played and finally is the same as an naive implementation when all diagonals have a stone. It suffices to store this information in two arrays, one storing the information
of the left diagonalas and the other the right diagonals. Notice that there is only $2\times board size -1$ left/right diagonals.

#### Labelling scheme
##### Left diagonals
Since there are more than one diagonal where stones can be placed to form a five in a row, we employ the following labeling scheme for labeling the diagonals. We shall demonstrate this scheme on a $15\times15$ board for convenience, although
this scheme can be generalized to any $n\times n$ board. Consider some placement of some stone $s$ on a $15\times 15$ board at **$p=(x,y)$ and take the difference $x-y = k$**. We consider the stone $s$ as belonging to the $k+(board size-1)$ th left diagonal. For example,
suppose player one placed a white stone on **$(3,8)$, then that stone belongs to the $9$ th left diagonal**, illustrated by the blue line in the following diagram.

<img src="/images/scheme_left_diagonal.png" width=50% height=50%>

##### Right diagonals
Consider another of some stone $s$ on a $15\times 15$ board at **$p=(x,y)$ and take the sum $x+y = k$**. We consider the stone $s$ as belonging to the $k$ th left diagonal. For example,
suppose player one placed a white stone on **$(7,9)$, then that stone belongs to the $16$ th right diagonal**, illustrated by the red line in the following diagram.

<img src="/images/scheme_right_diagonal.png" width=50% height=50%>

