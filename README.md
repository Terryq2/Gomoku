# Gomoku


## Board
For an $n\times n$ board we index the top left corner as $(0,0)$. A larger $x$ coordinate brings us more right relative to the origin. A larger $y$ coordinate brings us more down relative to the origin. This scheme is illustrated on the following $15\times15$ board.

<img src="/images/board.png" width=50% height=50%>

## Static Evaluations
## Evaluating horizontal and vertical lines
We track the number of stones in each horizontal and vertical linings of the board. When a stone is placed, we find the horizontal and vertical lining of the board for which that stone is placed and increment the associated variables by $1$.
```python
self.num_of_elements_in_rows: numpy.ndarray = numpy.zeros((self.board_size), dtype=int)
self.num_of_elements_in_cols: numpy.ndarray = numpy.zeros((self.board_size), dtype=int)
```
When making a static evaluation of the board we only score lines if they are occupied by at least one stone. In the following picture, for example, we would only evaluate the column at $x=8$ since it is the only column with greater than or equal to $2$ elements. We would not evaluate any rows
since no rows contain more than or equalt to $2$ elements. 



Furthermore, we record the minimum and maximum values of the $x$ and $y$ coordinates when placing stones on the board and only check for those columns and rows for values inside those constraints. Effectively, this puts a bound on the number of operations
that grows as stones are placed more spread out.



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

