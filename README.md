fuelsdk_search
-------------------------


Convenient search_filter building for FuelSDK using overloaded operators


## Description


Using the Salesforce Marketing Cloud SOAP API can be a pain; the particular pain-point this library seeks to alleviate
is in the use of `SimpleFilterPart`s and `ComplexFilterPart`s in search filters. It can be hard to recall the search
syntax for `SimpleOperator`s, especially since they're case sensitive in an ecosystem where almost nothing else is, and
the strings for different logical operators vary across the UI and APIs. This library provides a simple abstraction for
SOAP API search filter syntax using plain old python operators.

## Installation

```bash
# eventually
pip install fuelsdk_search
```

## Use

```python
In[1]: from fuelsdk_search import Simple as Prop
In[2]: (Prop('Name') == 'Joe Schmoe').build()
Out[2]: 
{'Property': 'Name',
 'SimpleOperator': <Operator.EQ: 'equals'>,
 'Value': 'Joe Schmoe'}
In[3]: (((Prop('Name') == 'Joe Schmoe') |
  ...:   (Prop('Name') == 'Jane Doe')) &
  ...:  (Prop('City') % 'St. ')).build()
Out[3]: 
{'LeftOperand': {'LeftOperand': {'Property': 'Name',
   'SimpleOperator': <Operator.EQ: 'equals'>,
   'Value': 'Joe Schmoe'},
  'LogicalOperator': <Operator.OR: 'OR'>,
  'RightOperand': {'Property': 'Name',
   'SimpleOperator': <Operator.EQ: 'equals'>,
   'Value': 'Jane Doe'}},
 'LogicalOperator': <Operator.AND: 'AND'>,
 'RightOperand': {'Property': 'City',
  'SimpleOperator': <Operator.LIKE: 'like'>,
  'Value': 'St. '}}
```

### Simple Operators

#### equals

```python
search_filter = (Prop('Key') == 'Value')
```

#### notEquals

```python
search_filter = (Prop('Key') != 'Value')
```

#### IN

Just pass a list-like object to `Prop.__eq__` operator

```python
values = {'Value1', 'Value2'}
search_filter = (Prop('Key') == values)
```

The `IN` simple operator will fail if the list has only one value; `Prop.__eq__` is smart enough to use plain old
`equals` if `len(value) == 1`

#### LIKE

```python
search_filter = (Prop('Key') % 'Value')
```
    
#### greaterThan

```python
search_filter = (Prop('Key') > 'Value')
```

#### greaterThanOrEqual

```python
search_filter = (Prop('Key') >= 'Value')
```

#### lessThan

```python
search_filter = (Prop('Key') < 'Value')
```

#### lessThanOrEqual

```python
search_filter = (Prop('Key') <= 'Value')
```

#### between

The `between` simple operator can be achieved by combining `<` and `>`. It also works for their `<=` variants because
SFMC isn't clear about how it handles bounds. 

```python
lower = 0
upper = 1
search_filter = (lower < Prop('Key')) <  upper
```

Bounds can be cancelled by comparing to `None`.

#### isNull

```python
search_filter = -Prop('Key')
# OR
search_filter = (Prop('Key') == None)
```

#### isNotNull

```python
search_filter = +Prop('Key')
# OR
search_filter = (Prop('Key') != None)
```

#### Inverting

All simple operators except `'LIKE'` can be inverted with the `Prop.__inv__` operator, `~`.
This can be a cheap way to effect a `NOT_IN` operator, one which isn't supported by the rest API. For example:

```python
search_filter = ~(Prop('Key') == ['Value1', 'Value2', 'Value3', 'Value4'])
```
Is equivalent to:
```python
search_filter = \
    (Prop('Key') != 'Value1') & \
    (Prop('Key') != 'Value2') & \
    (Prop('Key') != 'Value3') & \
    (Prop('Key') != 'Value4')
```

### Complex Operators

#### AND

```python
condition_a = (Prop('Key') == 'Value1')
condition_b = (Prop('Key') == 'Value2')

search_filter = condition_a & condition_b
```

#### OR

```python
condition_a = (Prop('Key') == 'Value1')
condition_b = (Prop('Key') == 'Value2')

search_filter = condition_a | condition_b
```

#### Many Comparisons

condition_a = (Prop('Key') == 'Value1')
condition_b = (Prop('Key') == 'Value2')

```python
condition_a = (Prop('Key') == 'Value1')
condition_b = (Prop('Key') < 'Value2')
condition_c = (Prop('Key1') % 'Value3')
condition_d = (Prop('Key2') == ['Value4', 'Value5'])

search_filter = (condition_a | condition_b) & condition_c & condition_d
```
