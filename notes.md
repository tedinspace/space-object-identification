# Notes from Pavlos Meeting

Pavlos' Comments:
- Add physics to the loss function?
- Inductive bias of some sort.
- There are physics associated with these orbital elements.
- Not pure neural net, but a physics-informed neural net.

Pavlos' Ideas:
- Extra/custom loss (predicting something else).
    - Equation: $D(r,v)-f(t)=0$
    - Pass $t$ as an input to the network, get $r, v$ to obtain the derivatives $r', v'$.
    - Loss: $\mathcal{L} = (D(r,v) - f(t))^2$
- Architecture of the NN (some relationship between the variables is already embedded into the architecture itself).
- Do some transformation to the data before passing it into the network.
- Pavlos wants us to predict trajectory information (lean more into the physics aspect).
- Post-modern analysis: for each object, we have $N$ observations. We have a NN that makes predictions for each 30k inputs. 
$$
    x^{(i)}_t \rightarrow \text{MODEL 1} \rightarrow p(y|x_t^{(i)}) \rightarrow \text{META MODEL}
$$

**Mixture of experts**, use a meta model to take the predictions, we could try aggregating via majority first then maybe a more complex aggregation technique.

Must be very careful about creating validation sets.

The meta model could be a RNN, we could also specify a max length for a fold.

Meta model could also utilize gates to learn which specific inputs they should prioritize.

Mixture models, stacking models, blending models.

If Pavlos were designing it:
$$
    x_t^{(i)} \rightarrow \text{NN}_1 p(y|x_t^{(i)}) \rightarrow \text{NN}_2 \rightarrow 
$$
Loss from NN_1 and NN_2 are combined somehow.