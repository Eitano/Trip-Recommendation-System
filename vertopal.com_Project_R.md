---
output:
  code_folding: hide
  df_print: paged
  fig_height: 5
  fig_width: 7
title: "Project : Corona virus and it's consequences"
---

## Final Project

## Assignment 1 - exploration of cases and concern data sets.

We would want to explore the data we received by the 5 core activities
of data analysis that we learned in class.

Our question is of type exploratory - we would want to check if there
are some relations between the different data sets we received.

We received the data sets:

-   Covid cases data set.

-   Concern data set.

-   Trump Tweets.

Our first assignment is to explore the data, so we would want to start
with that.`<br/>`{=html}We will explore the data by doing some
statistical analysis and plots for a better understanding, and for last
we will try to present the results as best as we can.

`{r setup, include=FALSE} knitr::opts_chunk$set(echo = TRUE)`

### Installations

**Note:** We have turned off the comments issued by the chunk, because
they are only prints of the system and irrelevant

``` {.{r}}
# install.packages("rtweet")
# install.packages("tidytext")
# install.packages("robotstxt")
# install.packages("lexicon")
# install.packages("stringr")
# install.packages("reshape")
#install.packages("multipanelfigure")
```

### Libraries

**Note:** We have turned off the comments issued by the chunk, because
they are only prints of the system and irrelevant. `<br>`{=html}

``` {.{r,warning=false,message=false}}
library(reshape)
library(tidyverse)
library(robotstxt)
library(rvest)
library(magrittr)
library(lubridate)
library(tidymodels)
library(tidytext)
library(textrecipes)
library(glue)
library(countrycode)
library(plotly)
library(tools)
library(broom)
library(ggridges)
library(corrplot)
```

## **Q1**

### Scraping the data and organize it

Here is a link to the site from which the information on the corona
cases was taken\
"<https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/United_States_medical_cases>"
`<br>`{=html}

First we check if the site allows us to access the table and perform
web-scraping

``` {.{r,warning=false,message=false}}
paths_allowed("https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/United_States_medical_cases")
```

**Note:** We have turned off the comments issued by the chunk, because
they are only prints of the system and irrelevant.

`<br>`{=html}

We will now perform web-scraping in order to extract thr table from the
web

``` {.{r}}
# wiki_url <- 'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/United_States_medical_cases'
# wiki_page <- read_html(wiki_url)
# Wiki_Cases <- wiki_page%>%
#   html_nodes ('#mw-content-text > div.mw-parser-output > div:nth-child(4) > table > tbody')%>%
#   html_table()
# Wiki_Cases <- as.data.frame(Wiki_Cases) # save the table as data frame
# Wiki_Cases
# saveRDS(Wiki_Cases, file = "data\\Wiki_Cases.rds")
```

`<br>`{=html}

Now we want to change the type of columns, it can be seen from the data
frame that confirmed cases is chr and not numeric.\
We will create a function to organize the data frame.

``` {.{r}}
Wiki_Cases<- readRDS("data\\Wiki_Cases.rds")
country<- unlist(Wiki_Cases[1,]) # save vector first row for future use
Wiki_Cases <- Wiki_Cases %>%
  filter(!Date %in% c('Date','Total','Refs','Notes'))%>%
  # fiter for removing the header of the table which appears many times inside the table
  mutate(Date=dmy(Date),Date.1=dmy(Date.1))  # mutate function for set column date as type date
```

`<br>`{=html}

### Function to convert all columns from char type to dbl type

``` {.{r}}
casting_dbl<- function(df){
  columns_name <- colnames(df) # get column names of df as vector to go over by iterations 
  for(i in 1:length(columns_name))
    {
    # apart from date column which we handle earlier, each column type char convert to dbl 
    if(typeof(df[, columns_name[i]])=="character") 
      {df[,columns_name[i]]<- as.numeric(gsub(",", "", df[,columns_name[i]]))}
    # we use gsub function for removing coma from numbers
    else{next}
    }
  df[is.na(df)] = 0 # all places with NA will have now zeros
  return(df)
}
```

`<br>`{=html}

### Function to convert change columns name

**Brief description of the function :**\
1) Use a dictionary from the web which converts abbreviations of states
to their names.\
2) Replace spaces between two word with "\_"\
3) Change the name of some columns which have at the origin table sub
columns\

`<br>`{=html}

Here is a link for the origin of abbreviations dictionary
'<https://bit.ly/2ToSrFv>'

``` {.{r}}
change_columns_names <- function(df , country){
  
        dict_abbrev<- read.csv('https://bit.ly/2ToSrFv')
        abv_country<- gsub(" ", "_", head(setdiff(country, colnames(df)),-2)) # extract difference 
        for (i in 1:length(abv_country)) 
        {if(abv_country[i] %in% dict_abbrev$abbreviation) # use %in% to look for country at abbreviations dict
          {abv_country[i]<- countrycode::countrycode(abv_country[i], 'abbreviation', 'state',custom_dict = dict_abbrev)}
        else{next}}
        
        abv_country<-gsub(" ", "_",abv_country) 
        search_for<- c('Date','Territories','Confirmed','Deaths','Recovered','Active') # columns with sub columns
        column_name <- colnames(df)
        res <- vector(mode="character", length=length(column_name)) # create new vector
        for (j in 1:length(search_for)) 
          {
          starts <-startsWith((column_name), search_for[j]) # use start with function to find name start with the same name
          for (i in 1:length(starts)) 
            {
            if(starts[i] == TRUE )
            {res[i] <-search_for[j]} # if TRUE means we find a match and we want to set the value at new vector 
          }
        }
        # now putting it all together
        for (i in 2:length(res)){
          if(res[i] == "") # if value is "" we didn't find a match so take from abv_country
          {res[i]<-paste(res[i], abv_country [i-1], sep = "")}
          
          else{res[i]<-paste(res[i], country[i], sep = "_")} # else append sub name column 
        }
        colnames(df)<-res
        return (df)
}
```

`<br>`{=html}

### Call all function to clean table

Now we will apply all function together, to get a fresh new clean
table.\
**Note**: we found that the table also contains territories and city
which not appear at dict_abbrev will append the separately

``` {.{r}}
clean_data<- function(df){
  country<- case_when(
          country=="DC" ~ "Washington_D.C",
          country=="GU" ~ "Guam",
          country=="MP" ~ "Northern_Mariana_Islands",
          country=="PR" ~ "Puerto_Rico",
          country=="VI" ~ "Virgin_Islands",
          TRUE ~ country)
  
  df_casting_dbl<-casting_dbl(df)
  df_change_columns<- change_columns_names(df_casting_dbl, country)
  return (df_change_columns)
}
Cases<- clean_data(Wiki_Cases)
Cases

# cases is sorted by columns names so we take region by [:]
West<-colnames(Cases)[2:14]
Midwest<-colnames(Cases)[15:27]
South<-colnames(Cases)[28:40]
Northeast<-colnames(Cases)[41:52]
Territories<-colnames(Cases)[53:56]
```

`<br>`{=html}

## **Exploration**

We will have a glimpse over the data for a better understanding.

``` {.{r}}
# glimpse(Cases)
```

We can see that the cases data frame has 2 different data frames:

-   **States cases** - this part represent data about cases that
    occurred in each day. each row represent the day and each column
    represent the state's cases per day.\
    This data frame contains also data collected about the territories
    of the US: Guam , Virgin Islands , Northen Mariana Islands and
    Puerto Rico.

-   **Total cases** - this part represent sum of cases of the US
    population by the categories:

    -   Daily reports for confirmed, deaths and recovered cases.

    -   Total reports for confirmed, deaths and recovered cases.

We noticed there are only 2 data types:

-   **dbl** - representing the the cases amount

-   **date** - representing the date.

`<br>`{=html}

### Separating to different data frames.

For start We would want to separate the 2 data frames for easier
working.\
After that, we would want to do some calculations over the regions of
the states, so we will create separated data frames for each region, and
a data frame of the states cases by each region.

``` {.{r}}
index1 <- c(1, 58:64)
Total_Df <- Cases %>% 
  select(all_of(index1))

index2 <- c(1:56)
Cases_States <- Cases %>% 
  select(all_of(index2))
```

We now have two data frames with different roles.

`<br>`{=html}

Let's check the dimensions of the df.

``` {.{r}}
dim(Cases_States)
dim(Total_Df)
```

All the data frames have 484 rows that represent the date of cases.\
The cases data frame have 56 variables that represent the states and
territories.\
The total_df data frame has 8 variables that represents total amount of
cases.\
We know that the rows represent data that was collected in each day , so
we will check the top and bottom of the data to understand when it
starts and when it ends.

`<br>`{=html}

Lets see the top and bottom of the cases states data frame

``` {.{r}}
Cases_States <- Cases_States %>% 
  arrange(Date) 

head(Cases_States, 5)
tail(Cases_States, 5)
```

First, we used the arrange function to arrange by the date, after we can
see our data starts at the 21.1.20 and ends at the 11.6.21.

`<br>`{=html}

#### Creating data frames for region

We want to create data frame representing the regions so we have a look
over the data from another angle.

``` {.{r}}
Region_Cases <- Cases %>% 
  mutate(Total_West = rowSums(.[2:14]), Total_Midwest = rowSums(.[15:27]),
         Total_South = rowSums(.[28:40]), Total_Northeast = rowSums(.[41:52]),
         Total_Territories = rowSums(.[53:56])) %>% 
  select(Date, Total_West, Total_Midwest , Total_South, Total_Northeast,
         Total_South, Total_Northeast, Total_Territories)
```

`<br>`{=html}

### Cleaning the data

Now that we organized the data we would want to check if there are
incorrect values in the data frame.

First, we will use the filter function to check for negative values.

``` {.{r}}
Cases_States %>% 
    filter_all(any_vars(.<0))
```

We see that we have 32 rows containing negative values.

we know that the data represent cases that occurred in the states, so
none of them should be negative.

At the beginning we thought the negative values are incorrect and we
should replace them to positive values, but after studding the reason
for the negative values we understand that they represent over count.

We planed to do statistical calculation over the data, so a better
choice would be to leave the negative values. Also we would want to
present some insights about specific days, so it might be better to
change the negative values to 0.

We decided to leave the negative values in the part that we do the
statistical analysis and after change the values to 0.

`<br>`{=html}

# Statistical analysis

We would want to do some statistical analysis over the data for a better
understanding.

We will create a function that will help us with those calculations.

``` {.{r}}
stats <- function(data){
    mean_data <- mean(data, na.rm = T)
    std_data <- sd(data ,na.rm = T)
    med_data <- median(data, na.rm = T)
    max_data <- max(data, na.rm = T)
    data_insigts <- c(mean_data,std_data,med_data,max_data) 
    return (data_insigts)
}
```

The function will calculate Mean, Std, Median and Max value for each
vector.

`<br>`{=html}

#### Analysis for states cases data frame

We would want to calculate statistic analysis for the cases data frame.

We used the **map_df function** for making the code shorter.

``` {.{r}}
#organize df for map function
Stats_Df <- Cases_States %>% 
  select(all_of(2:56))
#use stats function over all the data with map
Stats_Data <-map_df(Stats_Df, stats)
#Setting Estimate vector
Estimate <- c("Mean","Std","Median","Max")

#setting stats_data df
Stats_Data <- Stats_Data %>% 
  mutate("Estimate"= Estimate) %>% 
  relocate(Estimate)

Stats_Data
```

`<br>`{=html}

With those calculations we can have some insights: Let's see which state
has the highest number of cases in a single day

``` {.{r,warning=false,message=false}}
colnames(Stats_Data)[apply(Stats_Data,1,which.max)][1]
Stats_Data %>%
  summarise_if(is.numeric,max) %>%
  max()
```

It might be because California population is very large.\
But let's not assume things before we check the proportion of it's
population compeare with other states

-   We can explore the average number of cases in each state.

-   We can understand in which states the corona was stable and in which
    wasn't by the Std value - we have an assumption that in states with
    high std compared to the population count the corona affected the
    population in multiple waves.

-   We noticed that corona virus almost didnt affect the Northen Mariana
    Islands as the average number of cases per day is less then 1 and
    the maximum number of cases per day is 8.

`<br>`{=html}

We want to see the data from a different perspective, so we created a
box plot representing the region data. \`\`\`{r, fig.height= 8,
fig.width= 8} region_box_plot \<- Region_Cases %\>%
gather(key,value,-Date) %\>% ggplot(aes(x = reorder(key,value), y =
value, fill = key)) + geom_boxplot(notch = TRUE) +
scale_fill_manual(values=c("\#66CC99", "\#E69F00", "\#56B4E9",
"\#293352","\#CC6666")) + labs(x = "Regions", y = "Value", title = "Box
plot of total cases", subtitle = "Sum by each region and territory",
fill = "Regions") ggplotly(region_box_plot) %\>% layout(title =
list(text = paste0('Box plot of total
cases','`<br>`{=html}','`<sup>`{=html}','Summed by each region and
territory','`</sup>`{=html}')))


    ### Graph explanation:

    -   South region had the highest cases

    -   Territories area had the Least number of cases - an assumption would
        be because they are islands and it was easier for them to not allow
        entry to their areas.

    -   Median , q1 , q3 top and bottom cases per day.

    <br>

    #### Adding a Population data set

    Because the number of confirmed cases differs between states, where one of the reasons is the **size of the potential population to be infected**.\
    We normalized the total number of confirmed cases by th state population in it.\
    Here is a link for the source of the data set "https://www.infoplease.com/us/states/state-population-by-rank"
    <br>

    We will now perform web-scraping in order to extract the table from the
    web

    ```{r, message=FALSE, warning=FALSE}
    population_url <-"https://www.infoplease.com/us/states/state-population-by-rank"
    paths_allowed(population_url)

**Note:** We have turned off the comments issued by the chunk, because
they are only prints of the system and irrelevant.

`<br>`{=html}

``` {.{r}}
# Population_Df <- read_html(population_url)
# Population_Df <- Population_Df %>%
#   html_nodes ('#A0922497 > tbody')%>%
#   html_table()%>%
#   as.data.frame()%>%
#   mutate(Percent_of_Total= as.numeric(gsub("%", "", Percent.of.Total)),# replaced the percentages symbol %.
#   State= gsub(" ", "_", State), "Size_Population"= as.numeric(gsub(",", "", July.2019.Estimate))) %>%
#   select(Rank,State,Percent_of_Total,Size_Population)

# saveRDS(Population_Df, file = "data\\Population_Df.rds")
```

`<br>`{=html}

We would like to have a quick look at the data we will use glimpse

``` {.{r}}
Population_Df<- readRDS("data\\Population_Df.rds")
glimpse(Population_Df)
```

We can see that we have:

-   State's name column.

-   Rank column - this column is an indexing that organize the states by
    the size of population, where as the state with the highest
    population size, California, ranked by 1.

-   Percent of the state's population compare to the total population in
    the US.

-   Population count for each state.

`<br>`{=html}

We will use the head function to see the data

``` {.{r}}
head(Population_Df, n = 10)
```

`<br>`{=html}

**Note**: we added a function that scrapes the territories data from the
internet **by web scrapping**, because we didn't have it in the first
population.

``` {.{r}}
fetch_population <- function(selector){
  Territories_pop_url <- 'https://www.nationsonline.org/oneworld/US-states-population.htm'
  population <- read_html(Territories_pop_url)%>% 
  html_nodes (selector)%>%
  html_text()
  gsub(',','',population)%>%as.numeric()
}


Guam_selector <- 'body > div:nth-child(62) > div > div > div.ContCellPop'
Northern_Mariana_Islands_selector <- 'body > div:nth-child(63) > div > div > div.ContCellPop'
Puerto_Rico_selector <- 'body > div:nth-child(64) > div > div > div.ContCellPop'
Virgin_Islands_selector <- 'body > div:nth-child(65) > div > div > div.ContCellPop'


selectors <- c(Guam_selector,Northern_Mariana_Islands_selector,Puerto_Rico_selector,Virgin_Islands_selector)
get_population <- map_dbl(selectors,fetch_population)

Territor_pop_df <- tibble(
    State = Territories,
  Size_Population = get_population)

Territor_pop_df

Pop_Df <- Population_Df %>%
  select(State,Size_Population)
Pop_Df <- rbind(Pop_Df,Territor_pop_df)
Pop_Df
```

`<br>`{=html}

We built another 2 function for creating normalized cases count.

**Description of the functions :**

1.  append_factor - adding for each state or area another column
    representing region.

2.  apply_norm - function for creating the normalized cases count.

``` {.{r}}
append_factor<-function(df){
  res<-as.vector(df$State)
  for(i in 1:length(res)){
  if (res[i] %in% West){res[i]="West"}
  if (res[i] %in% Midwest){res[i]="Midwest"}
  if (res[i] %in% South){res[i]="South"}
  if (res[i] %in% Northeast){res[i]="Northeast"}
  if (res[i] %in% Territories){res[i]="Territories"}
  }
  df<-df %>% mutate(Region=res)
  return(df)
}

apply_norm <- function(df1,df2){
  new_df<- df1 %>%
  select_if(is.numeric) %>% map_df(sum) %>%
     pivot_longer(cols = everything(),names_to = "State", values_to = "Count") %>% 
        left_join(df2, by = "State") %>%
    mutate(Normed = round(Count/Size_Population,digits=3)) %>% 
    drop_na()
    new_df<-append_factor(new_df)
    return(new_df)
}

Normed_Cases <-apply_norm(Cases_States, Pop_Df)
```

**Note:** While using the function we removed Washington DC. because it
isn't a state or territory.

`<br>`{=html}

``` {.{r,warning=false,message=false}}
Normed_Cases[which.max(Normed_Cases$Size_Population), ]
```

\*\* Coming back to our understand that the amount of confirmed cases
was the highest at US was at California, now we can be sure that in fact
base on another data set that California has the maximum inhabitants at
USA. \*\*

`<br>`{=html}

### Plots

#### Bar plot representing the cases normalized to population size by each region

We would plot the sum of cases in each state normalized by their
population size and present them while we use the facet wrap function
for separating for each region.

\`\`\`{r, fig.height= 8, fig.width= 8} ggplot(data= Normed_Cases, aes(x
=Normed , y = reorder(State,Normed) , fill = Region))+ geom_bar(stat =
"identity", color = "black", position="stack") +
scale_x\_continuous(labels=scales::percent) +
scale_fill_manual(values=c("\#66CC99", "\#E69F00",
"\#56B4E9","\#CC6666", "\#293352"))+ facet_wrap(\~Region, ncol =
2,scales = "free") +

geom_vline(data=Normed_Cases, aes(xintercept=mean(Normed),
color=Region), color="red", size=0.8)+

labs(x = "Cases ratio", y = \" ", title ="Bar plot of the cases ratio in
each state", subtitle ="Divided to each region and normalized by
population count", fill ="Region\")


    ### Graph explanation:

    -   The states with the highest ratio of cases compared to population
        are:

        -   Midwest region - North Dakota

        -   Northeast region - Rhode Island

        -   West region - Utah

        -   South region - Tennessee

    -   In most of the states more then 5% of the population was affected by
        the corona.

    -   Compared to the other regions the Midwest region population was
        affected the most.

    -   Hawaii is the state the was affected at the lowest level compared to
        all the states.

    -   We added a red line representing the mean normalized cases count for
        an observation for which states are above or under the mean.

    <br>

    ### Exploration for total cases df

    We would want to present a plot that shows the change by count of each
    column that represent total counting in the total df. We will create a
    line plot that represent the changes over time for the total count
    normalized by the total population count.

    For start lets have a glimpse over the df and explain the columns that
    we have
    ```{r}
    glimpse(Total_Df)

**Note:** we explained the columns while we glimpsed cases df.

`<br>`{=html}

We would want to add the data frame some new variables that can help us
in further calculations, We will add: total and daily ratio for death
and recovery cases.

``` {.{r}}
New_Total_Df <-Total_Df %>% filter(Confirmed_Daily>0) %>% 
  mutate(Total_Death_Ratio =Deaths_Total/Confirmed_Total,
         Daily_Death_Ratio =Deaths_Daily/Confirmed_Daily,
         Total_Recover_Ratio = Recovered_Total/Confirmed_Total,
         Daily_Recover_Ratio = Recovered_Daily/Confirmed_Daily) 
New_Total_Df 
```

`<br>`{=html}

Plot:

``` {.{r}}
plot_ly(data= New_Total_Df %>% 
  gather(key,value,Deaths_Total,Confirmed_Total,Active_Total,Recovered_Total)) %>%

  add_trace(
      x = ~ Date,
      y = ~  value/sum(Pop_Df$Size_Population), #calculating total population
      color = ~ key,
      type = "scatter",
      mode = "lines",
      text = ~paste("Date: ", Date,
                    "</br>Accumulate number  : ", value,
                    "</br>Total_Population: ", sum(Pop_Df$Size_Population)),
      name = ~key) %>% 

      layout(title = paste("Line plot representing the ratio of active, confirmed, deaths and recoverd cases",
                       '<br>', "Normalized by the number of population in the US"),
             yaxis = list(title = "Ratio",  range = c(0, 0.05)), 
             xaxis = list(title = "Date"),
             legend = list(x = 0.99, y = 1))
```

### Graph explanation:

-   We can see that the confirmed cases reached over 4% of the
    population.

-   The deaths ratio is less then 1%.

-   The recovery rate that change almost like the confirmed ratio.

-   the active cases ratio time line that has a peak between 1/1/21 to
    the 1/7/21.

`<br>`{=html}

## Civiqs poll data frame exploration

We would start by loading the csv file

``` {.{r,warning=false,message=false}}
Civiqs_Poll<- read_csv('data\\civiqs_poll.csv')  # open file 
if("date" %in% colnames(Civiqs_Poll)==TRUE)
  {Civiqs_Poll$date <-as.Date(Civiqs_Poll$date, format = "%m/%d/%Y")} # cast date col from chr type to date type

Civiqs_Poll<- Civiqs_Poll %>% 
  rename_with(str_to_title) # convert capital letter in each cols name
Civiqs_Poll
```

`<br>`{=html}

Let's have glimpse over the data for a better understanding

``` {.{r}}
glimpse(Civiqs_Poll)
```

We have 4 columns which contains:

-   Date.

-   Democrat's concerns presented in percentage.

-   Republicans concerns presented in percentage .

-   The difference in concern between both parties calculated by the
    formula: Diff = Dem - Rep.

We noticed from the glimpse function that the concern value doesn't
start from 0, it starts for Rep column from -48 and for Dem column at
35.

`<br>`{=html}

Lets see the top and bottom of the data frame

``` {.{r}}
Civiqs_Poll %>% 
  head()
```

``` {.{r}}
Civiqs_Poll %>% 
  tail()
```

We see that the data we have starts at the 2020-02-25 and ends at the
2020-04-05, so we have a little bit more than a month of the concern
ratio of both parties.

`<br>`{=html}

lets see the dimension.

``` {.{r}}
dim(Civiqs_Poll)
```

We have 41 rows of data meaning 41 days.

`<br>`{=html}

We would want to plot the concern of both parties to have a better look.
\`\`\`{r, message=FALSE, warning=FALSE}

plot_ly(data= Civiqs_Poll) %\>% add_trace( x = \~ Date, y = \~ Dem, type
= "scatter", mode = "lines+markers", line = list(color="steelblue"),
marker = list(color="steelblue"), hoverinfo = 'text', text =
\~paste("`</br>`{=html}Dem:", Dem, "`</br>`{=html}Date:", Date), text =
\~paste("Date:", Date), name = "Democrats") %\>%

    add_trace(
      x = ~ Date,
      y = ~  Rep,
      type = "scatter",
      mode = "lines+markers",
      line = list(color="red"),
      marker = list(color="red"),
      hoverinfo = 'text',
      text = ~paste("</br>Rep:", Rep,
                    "</br>Date:", Date),
      name = "Republicans") %>% 

      layout(title = paste("Concern ratio in each Party",
                       '<br>', "Between dates 2020-02-25 to 2020-04-05"),
             yaxis = list(title = "Concern (%)",ticksuffix = "%", range= c(-70, 100)), 
             xaxis = list(title = "Date"),
             legend = list(x = 0.99, y = 1),
             hovermode = "compare")


    **Note:** We have turned off the comments issued by the chunk, because
    they are only prints of the system and irrelevant. <br>

    ### Graph explanation:

    As we can see the scales goes from a minus value to 100%, we can
    understand that the scales goes from -100% meaning no concern to 100%
    meaning a full concern. We noticed that we have an increase in concern
    by both parties that starts at the 7-8/3/2020 for 2 weeks more or less.
    Lets try to understand why. While exploring the cases data frame we
    noticed we have data about deaths cases that happened during the
    pandemic, we believe the death rate by the virus might affect the
    concern level of both parties as it affects both of them. So we would
    want to calculate the death rate in the same time range of the concern
    time range. We will calculate it by using the formula: death rate =
    death cases / total cases.

    <br>



    ### Graph showing the diff concern with changes during the plague

    We would like to link our two data sets, and explore if the increase in
    the number of new cases per day and in the number of daily deaths can
    explain the difference in the concern of the Democratic and Republican
    parties.
    ```{r fig.width=9}
    plot_ly(data= Cases %>% filter(Date<="2020-04-05" & Date >="2020-02-25")) %>%
      
      add_trace(
          x = ~ Date,
          y = ~ Confirmed_Daily/300,
          type = "scatter",
          mode = "lines+markers",
          hoverinfo = 'text',
          text = ~paste("</br>Confirmed_Daily:", Confirmed_Daily,
                        "</br>Date:", Date),
          name = "Confirmed_Daily",
          line = list(color = "black"),
          marker = list(color = "black")) %>%
      
      add_trace(
          x = ~ Date,
          y = ~ Deaths_Daily/10,
          type = "scatter",
          mode = "lines+markers",
          hoverinfo = 'text',
          text = ~paste("</br>Deaths_Daily:", Deaths_Daily,
                        "</br>Date:", Date),
          name = "Deaths_Daily",
          line = list(color = "hotpink"),
          marker = list(color = "hotpink")) %>%
      
       add_trace(data=Civiqs_Poll,
          x = ~ Date,
          y = ~ Diff,
          type = "scatter",
          mode = "lines+markers",
          hoverinfo = 'text',
          text = ~paste("<br>Diff:", Diff,
                        "</br>Dem:", Dem,
                        "</br>Rep:", Rep,
                        "</br>Date:", Date),
          name = "Diff",
          line = list(color = "steelblue"),
          marker = list(color = "steelblue")) %>% 


      layout(title = "Difference in support along with the spread of the plague",
             yaxis = list(title = "Number"), 
             xaxis = list(title = "Date"),
             legend = list(x = 0.99, y = 1),
             hovermode = "compare")

### Graph explanation:

Let's divide the tendency of diff line to 3 stages.\

1)  **First Stage:** It can be noted that when the number of new cases
    and the number of deaths per day is low, the difference in opinions
    is high which can explain a polarization in the opinions of both
    parties.

2)  **Second Stage:** As the number of deaths per day and the verified
    increases, it can be seen that the difference in the opinions of the
    two parties decreases significantly, which can explain the common
    concern of the two parties regarding dealing with the party in US.

3)  **Third Stage:** At the end of the graph where there is a kind of
    stabilization in the difference between the parties that occurs
    along with the decrease in mortality and the decrease in the number
    of infected per day.

**Note:** we chose to divide some number just to explain a tendency and
how it impact on other tendency. The real number is presented in text
box.\

``` {.{r}}
p <- New_Total_Df %>% 
  select(Date,Total_Death_Ratio,Daily_Death_Ratio) %>%
  gather(key,value, -Date) %>% 
  ggplot(aes(x = Date, y = value, color = key)) +
  scale_x_date(limits = as.Date(c("2020-02-25","2020-04-05"))) +
    scale_y_continuous(labels=scales::percent) +
  geom_line() +
  labs(x = "Date", y = "Death ratio (%)", title = "Line plot representing Death Ratio", subtitle = "Over the USA population between dates 2020-02-25 to 2020-04-05")
ggplotly(p)%>% 
   layout(title = list(text = paste0('Line plot representing Death Ratio',
                                    '<br>',
                                    '<sup>',
                                     'Over the USA population between dates 2020-02-25 to 2020-04-05','</sup>')))
```

### Graph explanation:

We can see that we have a steep rise in the death ratio that starts at
the begging of march, that can explain the increase in concern for both
parties.

We would want to check if the death cases can cause the increase in
concern. We will create a plot combing the daily death and the concern
ratio for both parties.

`<br>`{=html}

**Brief description for the plot :**

1.  We reset the level of concern to 0 for both parties in order to test
    their rise

2.  We join the concern and total_df by date to get the information only
    at the specific dates we have.

3.  We used gather function to do pivot longer for the 2 parties data

4.  we created a dot plot with regression presenting the increase of
    concern by the increase in daily death cases.

`{r ,message=FALSE, warning=FALSE} p <- Civiqs_Poll %>%    mutate(Dem = (Dem-35)/100, Rep = (Rep+58)/100) %>%    left_join(Total_Df, by = "Date") %>%    gather(key,value,Rep,Dem) %>%    ggplot(aes(y =value, x = Deaths_Daily, color = key)) +   scale_y_continuous(labels=scales::percent) +   geom_point() +geom_smooth(se=F) +   labs(y = "Concern Rate", x = "Death Daily", title = "Increase in mutal concern for both parties", color = "Party") ggplotly(p) %>%     layout(title = list(text = paste0('Dot plot representing the increase in concern for both parties',                                     '<br>',                                     '<sup>',                                      'While daily deaths number goes up','</sup>')))`

### Graph explanation:

It can be seen that while the death daily count increased the concern
ratio for both parties increased dramatically. The concern ratio in the
Republican party has an increase of almost 80% and the Democratic party
by 40%.\

**Note:** We have turned off the comments issued by the chunk, because
they are only prints of the system and irrelevant

`<br>`{=html}

`<br>`{=html}

`<br>`{=html}

## **Q2**

**Fetch concern data (Civiqs_Poll csv): **

Using function ymd to convert (the column 'Date' from character to date
type, And week()) in order to fetch the week for every date.\
Lastly look at the head of the data for better understanding.

``` {.{r}}
Concern<- Civiqs_Poll %>% 
  mutate(Week=week(ymd(Date)))
Concern%>%head
```

### Donald trump tweets:

Read from the data folder.\
First, look at the columns with glimpse() function:

``` {.{r}}
Trump_Tweets<- readRDS("data//trump.rds")
glimpse(Trump_Tweets)
```

\*\*We have 1,549 rows, 6 columns - The tweet's date, The tweet's
favorites quantity, Id tweete, If the tweet is retweet, and the content.

### Arrange the dataset a littel bit:

Adding week column and separate the Date to date and time.\
Use str_to_title() function in order to put capital letters at the first
character for each column.\
Select only the columns we are interested in for our's work.\
Lastly look at the the dataframe for better understanding.

``` {.{r}}
Trump_Tweets <-separate(Trump_Tweets, date, c("Date", "Time"), sep = " ")%>%
  mutate(Date=as.Date(Date),retweets=as.numeric(retweets))%>% 
  rename_with(str_to_title)%>%
   mutate(Week=week(ymd(Date)))%>%
  select(Date, Text, Id, Week)

Trump_Tweets%>% head
```

### Visualize the data (Tweets during the concern poll):

\`\`\`{r fig.width=10} plot_ly(Trump_Tweets , x= \~Date, type =
"histogram", name = "Tweets quantity") %\>%

add_trace(data= Concern, x = \~ Date, y = \~ Diff, type = "scatter",
mode = "lines", name = "Diff", line = list(color = "violet")) %\>%

add_trace(data= Concern, x = \~ Date, y = \~ Dem, type = "scatter", mode
= "lines", name = "Dem", line = list(color = "seagreen1")) %\>%

     add_trace(data= Concern, x = ~ Date,
            y = ~ Rep,
            type = "scatter",
            mode = "lines",
            name = "Rep",
            line = list(color = "red")) %>%

layout(title = "`<b>`{=html}Tweets quantity and concern level per
day:`</b>`{=html}`<br>`{=html}Histogram-Tweets
quantity.`<br>`{=html}Curves - Concern for party and their difference.",
xaxis = list(title = "Date", zeroline = FALSE), yaxis = list(title =
"Tweets quantity, Concern level",range=c(-60,250), zeroline = FALSE))


    ### Graph explanation:

    At fist, The Republicans were not concerned, this makes sense given the fact that they are Trump's party which from the beginning was very disrespectful to Covid.\
    This continued in the first days, but then there was a very sharp rise in their level of concern and slowly they approached the level of the Democrats.\
    The Democrats were way more concerned from the begging, but the slope of their trend line is quite similar to the Republicans (but lower), what brings the difference to decrease most of the time.\
    About the tweets quantity - We can see few peeks, **one of them is way bigger then the others (We found from research that in this times, a lot of countries in the world confirmed their first case  of Covid)**, in this range of time we can see a steep rise in the concern level of both Democrats and Republicans.\

    **Note:** Axis Y starts from less than -50 instead of zero, Because it's the lowest concern value - The Republicans concern at the begging of the epidemic, at first their amount of concern was -57 (Just 21.5% of them were concerned, While 78.5 were not worried about COVID)

    <br>

    ### Cleaning the text tweets:

    Catch patterns with regex and clean the data in order to get the content of the text. 
    Filter rows that do not contain text after produce the regex.
    And take a brief look at the result:

    ```{r}

    Trump_Tweets <- Trump_Tweets %>%
      mutate(Text=tolower(Text))%>% #convert to lower letters.
      mutate(Text = str_replace_all(Text, '@\\w+|https?://.+|\\d+\\w*\\d*|#\\w+|[^\x01-\x7F]',''))%>%
      mutate(Text = str_replace_all(Text, ' ?(f|ht)(tp)(s?)(://)(.*)[.|/](.*)', ''))%>%#Remove URLs
      mutate(Text = str_replace_all(Text, '&amp;', 'and'))%>%# Replace "&" character reference with "and"
      mutate(Text = str_replace_all(Text, '[[:punct:]]', ''))%>% # Remove puntucation, using a standard character class
      mutate(Text = str_replace_all(Text, '^rt:? ', ''))%>%# Remove "RT: " from beginning of retweets
      mutate(Text = str_replace_all(Text, '@[[:alnum:]]+', ''))%>%# Remove mentions e.g. "@my_account"
      mutate(Text = str_replace_all(Text, '#[[:alnum:]]+', ''))%>%# Remove hashtags
      mutate(Text = str_replace_all(Text, '\\\n', ''))%>%# Replace any newline characters with a space
      mutate(Text = str_replace_all(Text, '\\$',''))%>% #remove dollar sign
      mutate(Text = str_replace_all(Text, '\\+',''))%>% #remove + sign
      mutate(Text = str_replace_all(Text, 'http',''))%>% #remove http sign
      mutate(Text = str_replace_all(Text, '[[:digit:]]',''))%>%
      filter(lengths(strsplit(str_trim(Text), " "))!=0)

    Trump_Tweets$Text%>%head

### Let see the frequency of the words amount per tweet:

For this plot we will make a new column (Text_Len) which is the length
of the text. \`\`\`{r fig.width=10} Tweets_with_txt_len \<-Trump_Tweets
%\>% mutate(Text_Len=as.numeric(lengths(str_split(str_trim(Text,"both"),
\" \"))))

# color_for_week = Tweets_with_txt_len%\>%unique(select(Week)))

ggplotly(ggplot(Tweets_with_txt_len, aes(x=Text_Len,
color=as.factor(Week))) + geom_histogram(alpha=0.5,position="identity",
bins =50, binwidth=1)+ geom_vline(data=Tweets_with_txt_len,
aes(xintercept=median(Text_Len)), color="gold", size=0.7)+

labs(title = "`<b>`{=html}Distribution of the words quantity per
tweet`</b>`{=html}`<br>`{=html}Red-Retweeted tweet \| Blue-Original
tweet \| Golden line-Median", x = "Tweet length (words quantity)", y =
"Tweets amount")+ guides(color=guide_legend("Week:")))



    ### Graph explanation:

    We can see big changes between weeks (It reminds normal distribution with expectation=20, and left tail if we make uniscretization).\
    As the time past, there is an increase in the length of the tweets (week 8 and 14 can mislead because the have less information).\
    At week 12 we can see a lot of words said (maybe because of panic) at week 13 still we have big amount of words said relative to weeks 8-11.

    **Note:** 
    Golden line - median.

    <br>

    ### Reaserch:

    It looks like as the time past, more and more words said in tweets, what lead us to think that the amounts of words said can be a predective.
    Let's research what about sentiment, looking at the most meaningful words.


    ### Step1: (separate text to ngrams)

    **Separate the data set into bigrams and one grams and take out the stop words:**
    ```{r}
    Trump_Tweets<-Trump_Tweets%>%
      unnest_tokens(Bigram, Text, token = "ngrams", n = 2, n_min = 1)%>% # drop rows with stop words
      anti_join(stop_words, by = c("Bigram" = "word"))

    Trump_Tweets

`<br>`{=html}

### Step2: (get tf_idf)

**Tf_Idf** First, count quantity of bigram per tweeter id and Bigram:

``` {.{r}}
Bigram_Frequency <-Trump_Tweets%>%
  group_by(Bigram,Id,Date) %>%
  summarise(n = n(), .groups = "drop")
```

`<br>`{=html}

Select the 5000 ngrams highest tf_idf scores.\
Fetch tf_idf score for every word. Note- Id is tweet ID.

``` {.{r}}
Tf_Idf <- Bigram_Frequency%>%
  bind_tf_idf(Bigram, Id, n)%>% #Fetch tf_idf score for every word. Note- Id is tweet ID.
  dplyr :: rename(Tf_Idf = tf_idf)%>%
  select(Date,Bigram,Tf_Idf)%>% 
  arrange(desc(Tf_Idf))%>%
  head(5000)
Tf_Idf
```

**Note:** Package 'reshape', Override the function rename, So using
specifics 'dplyr' rename function. `<br>`{=html}

### Step3: (get sentiment)

**Get sentiment ("bing"-positive/negative) for every ngram.** And Fetch
week in oreder to plot the data by week.

``` {.{r}}
Sentiment <- Tf_Idf %>%
  inner_join(get_sentiments("bing"), by = c("Bigram"="word"))%>%
  filter(Bigram!='trump') #It gives the word 'trump' positive sentiment and for our work it bit misleading.
```

### Plot the bigram with Tf_Idf score per week

``` {.{r}}
#Plot tfidf for words for every week : 
Sentiment <- Sentiment%>%
            mutate(Week=week(ymd(Date)))
plotlist = list()
min_week <- Sentiment%>%select(Week)%>%min
max_week <- Sentiment%>%select(Week)%>%max
for (i in min_week:max_week) 
  {
    p <- ggplot(Sentiment%>%
              filter(Week==i),
          aes(y = Bigram, x = Tf_Idf, fill = sentiment))+
  labs(title = paste('Week:',i), x = "Tf Idf score", y = "") +
    geom_col(show.legend = F) +
    facet_grid(Week  ~ ., scales = 'free')
    plotlist[[i-7]] = ggplotly(p)
  }
htmltools::tagList(setNames(plotlist, NULL))

```

### Graph explanation:

We can see an unbalanced results in terms of sentiment, there are weeks
were the concern increased but there were a lot of positive words with
high score of Tf Idf, what bring us to think that not to look if the
word is negative or positive, but still make sure it's one of them,
because we belive that meaningful words will be more predective.

`<br>`{=html}

### **Hypothesis:**

Based on the exploration it can be seen that as time goes on, the amount
of tweets increases and the level of concern also increases (in both
parties, we will concentrate on Democrats).\
**Our assumption is this** - an increase in the time and amount of words
that have a positive / negative emotion (words with strong content)
spoken that day can predict the value of concern for that day among
Democrats\
Note - We chose to concentrate on Democrats because they don't support
Trump, so it makes sense that they would be suspicious of anything he
does. Especially when he initially underestimated the epidemic.\
We assume that as time goes on and you hear bad things about COVID in
the world, and the more sensitive words are said, then they will be more
concerned.\
To do this, we will only use words with positive or negative emotion, of
which we will only use 5000 words with the highest TFIDF score, in order
to use the most prominent words. Considered 3 more columns - the amount
of words per day, after the filtering we mentioned, the average TFIDF
for that day, and a log of the number of days that have passed since the
beginning of our data.

### Step1: (produce variables - words quantity and average tf_idf per day)-

`<br>`{=html}

**words quantity** Create new column - Normalized_Quantity, Which is the
sum of positive and negaitve bigrams, divide by the maximum quantity.\
divided by the absolute sum.

``` {.{r}}
Normalized_By <-  max(Sentiment 
                      %>%group_by(Date)
                      %>%summarise(n = n())
                      %>%select(n))

Bigrams_Quantity <- Sentiment %>%
  group_by(Date)%>%
  summarise(Normalized_Quantity = n()/Normalized_By)#normalized the count with the maximum count
Bigrams_Quantity%>% arrange(Date)
```

`<br>`{=html}

**average tf_idf** Calculate average tf_idf for bigrams with
positive/negative sentiment per day

``` {.{r}}
Avg_Tf_Idf <- Sentiment%>%
  group_by(Date)%>%
  summarise(Average_Tf_Idf = mean(Tf_Idf))
Avg_Tf_Idf
```

`<br>`{=html}

### Step2: (join all)

Join all of the in order to get the whole data for the model:

``` {.{r}}
Data_For_Model<-Avg_Tf_Idf%>%
  inner_join(Bigrams_Quantity, by = "Date")%>%
  inner_join(Concern, by = "Date")
Data_For_Model
```

`<br>`{=html}

### Step3: (add col - log days past)

Calculate - Log Days Past, formula: log(date-first day)

``` {.{r}}
Fist_Day <- Data_For_Model%>% summarise(min(Date))

Data_For_Model <- Data_For_Model%>%
  mutate(Log_Days_Past=log(as.numeric(Date)-as.numeric(Fist_Day)+1))
Data_For_Model
```

`<br>`{=html}

### Step4: (look for variables with good correlation - later we will lok also at pearson's R as asked)

Select the variables we will use in the model.\
Try different combinations and calculate their Pearson's R - just to
look for which variables could give good (later we will check it on the
test data) :

``` {.{r}}
cor(Data_For_Model$Normalized_Quantity+Data_For_Model$Log_Days_Past, Data_For_Model$Dem, method="pearson")
cor(Data_For_Model$Normalized_Quantity*Data_For_Model$Log_Days_Past, Data_For_Model$Dem, method="pearson")
cor(Data_For_Model$Average_Tf_Idf+Data_For_Model$Log_Days_Past, Data_For_Model$Dem, method="pearson")
cor(Data_For_Model$Average_Tf_Idf*Data_For_Model$Log_Days_Past, Data_For_Model$Dem, method="pearson")
```

`<br>`{=html}

### Take a look at the connection between the variables average sentiment and Diff concern (concern as function of tweets)

(Plot the points at red dots with geom_point, and draw a curve between
the dots using splines).

``` {.{r}}
ggplotly(ggplot(data=Data_For_Model, aes(x = Normalized_Quantity+Log_Days_Past, y = Dem)) +
 geom_point(color = "red", alpha = 0.7) +
 geom_smooth(method='lm', formula= y~x, se=FALSE)+
 labs(x = "Predictor var(Normalized_Quantity+Log_Days_Past)", y = "Predicted var(Democrats concern)", title = ""))
```

### It seems that linear regression could work.

`<br>`{=html}

### Create Model:

Setting seed to get always the same results (same random).\
Split the data into train and test with proportion of 3/5 (chosen by us
for more information at the test.)

``` {.{r}}
set.seed(1000)
Data_Split <- initial_split(Data_For_Model, prop = 5/7) # prop = 3/4 by default
Train <- training(Data_Split)
Test    <- testing(Data_Split)

#Declare on linear regression model with the engine 'lm'.
Cross_Val_Mod <- linear_reg() %>%  set_engine("lm")
```

`<br>`{=html}

### Step1: Make Recipe -

Relate Date column as id, and remove columns - Dem, Rep,. Finally remove
zero variance variables.

``` {.{r}}
Rec <- recipe(Dem ~ Normalized_Quantity+Log_Days_Past ,data = Train)%>%
                  step_zv(all_predictors()) #remove zero variance variables
Rec
```

### Step2: Create workflow -

Add the model and the recipe

``` {.{r}}
Wflow <- workflow() %>%
  add_model(Cross_Val_Mod) %>%
  add_recipe(Rec)
```

### Step3: k fold cross validation -

Make k fold cross validation from the train data with 5 folds and
repeats 3 time:

``` {.{r}}
Folds <- vfold_cv(Train, v = 5, repeats = 3)
```

### Step4: Produce the resamples -

Produce the resamples and fit it,\
Save the predictions -just to take a peek (The information that really
matters is the test predictions).\
And fit_rs conatins the regression for each fold.

``` {.{r}}
Fit_Rs <- Wflow %>%  fit_resamples(Folds,control = control_resamples(save_pred = TRUE))
```

`<br>`{=html}

**Metrics (summarized): ** Look at the metrics for the cross
validation,\
Rename columns and select specific for better view :

``` {.{r}}
collect_metrics(Fit_Rs)%>%
  dplyr::rename(Kfolds_Quantity=n,Metric=.metric, Mean=mean,  Standard_Deviation_Error=std_err)%>%
  select(Kfolds_Quantity,Metric, Mean,  Standard_Deviation_Error)
```

**Note:** Package 'reshape', Override the function rename, So using
specifics 'dplyr' rename function.

`<br>`{=html}

**Metrics : ** Look at the metrics separate for each fold:

``` {.{r}}
collect_metrics(Fit_Rs, summarize = FALSE)%>%
  dplyr::rename(Repeat=id,Fold=id2,Metric=.metric, Vlaue=.estimate)%>%
  select(Repeat,Fold,Metric, Vlaue)
```

**Note:** Package 'reshape', Override the function rename, So using
specifics 'dplyr' rename function.

`<br>`{=html}

**folds results:** Look at the predictions for each fold and repeat:

``` {.{r}}
Train_Pred <- collect_predictions(Fit_Rs)%>%
  dplyr::rename(Repeat=id,Fold=id2,Prediction = .pred,True_value = Dem)%>%
  select(Repeat,Fold,Prediction,True_value) %>%
  mutate(Abs_Error = abs(Prediction-True_value))

Train_Pred
```

**Note:** Package 'reshape', Override the function rename, So using
specifics 'dplyr' rename function.

`<br>`{=html}

### Visualize folds results:

Just to take a peek at the folds in order to insure we don't have great
variance or something we didn't expect to receive.\

``` {.{r}}
ggplotly(ggplot(Train_Pred, aes(x=Fold, y=Abs_Error, fill=Repeat)) +
    geom_boxplot()+labs(x = "Fold", y = "Absolut error", title = "Compare folds"))
```

### Graph explanation:

Most of error values between 1-10, the repeats brings similar results
for the same fold.\
It seems that most of the folds gives us quite similar results in total.

`<br>`{=html}

**Note:** Ther are few outliers. It make sense since we made 3 repeats
for 5 folds. The information that really matters is the test as we said
before.

`<br>`{=html}

### Fit on the training set and evaluate on test set:

``` {.{r}}
Rf_Fit <- Wflow %>%
  last_fit(Data_Split)
#Take the test peformance
Test_Performance <- Rf_Fit %>% collect_metrics()
Test_Performance
```

`<br>`{=html}

**Fetch the predictions:**

``` {.{r}}
Test_Predictions <- Rf_Fit %>% collect_predictions()%>%
  dplyr::rename(Data=id,Prediction = .pred,True_value = Dem,Row_num=.row)%>%
  select(Row_num,Data,Prediction,True_value) %>%
  mutate(Abs_Error = abs(Prediction-True_value))
Test_Predictions %>%
  arrange(Row_num)
```

**Note:** The coloumn called train/test split but it's only for the
test\
(as claims this article - (credit)\
http://www.rebeccabarter.com/blog/2020-03-25_machine_learning/\#evaluate-the-model-on-the-test-set)\
**By Rebecca Barter** (Postdoctoral Scholar, Department of Statistics,
University of California, Berkeley)\
Even though It seems to be a reliable source, lets check it using join
with the test data frame.

`<br>`{=html}

**Look at the results:**

``` {.{r}}
Test_Results <- Test_Predictions %>% 
  select(Row_num,Prediction,True_value,Abs_Error)%>%
  inner_join(Data_For_Model %>% 
               mutate(Row_num = row_number())%>%
               select(Date,Normalized_Quantity,Log_Days_Past,Row_num), by="Row_num")%>%
  select(Date,Normalized_Quantity,Log_Days_Past,Prediction, True_value,Abs_Error)
Test_Results
```

`<br>`{=html}

The joined dataframe didn't seperate the column "True_value" - means
that the values of "True_value" at the both table were the same, and
it's still contains the same number of rows, let's assure using the
function nrow() :

``` {.{r}}
Test_Results%>% nrow == Test%>%nrow  
```

`<br>`{=html}

### Evaluate results:

### Plot the predictions with the with the true values:

`{r, warning=FALSE, message=FALSE} a<-ggplot(data=Test_Results, aes(x = Date, y = True_value)) +   geom_point(aes(x = Date, y = True_value),color = "blue", alpha = 0.7)+   geom_point(aes(x = Date, y = Prediction),color = "red", alpha = 0.7) +   geom_smooth(formula = y ~x,method = 'loess',span = 0.35,se = FALSE)+  labs(x = "Date", y = "Democrats concern", title = "Test results: Predictions Vs. Ground True per day,<br>Red points - predictions | Blue points - True values") ggplotly(a)`

### Graph explanation:

We drew a curve between the true values and colored the predtions in red
to emphasize the distance between randomial function that go through the
true values and the predictions.

`<br>`{=html}

**Note:** The data is from the first day to the final day at the test
data set.

`<br>`{=html}

### **Pearson's R :**

``` {.{r}}
cor.test(Test_Results$Prediction, Test_Results$True_value, method="pearson")
```

`<br>`{=html}

### Plot the error series:

\`\`\`{r, fig.width=10, fig.height=10}

plot_ly(data= Test_Results) %\>%

add_trace( x = \~ Date, y = \~ Abs_Error, type = "scatter", mode =
"lines+markers", name = "trace", line = list(color = "red"), marker =
list(color = "green")) %\>%

add_trace( x = \~ Date, y = \~ mean(Abs_Error), type = "scatter", mode =
"lines+markers", name = "Mean absolut error", line = list(color =
"blue"), marker = list(color = "blue")) %\>%

add_trace( x = \~ Date, y = \~ median(Abs_Error), type = "scatter", mode
= "lines+markers", name = "Median absolut error", line = list(color =
"pink"), marker = list(color = "pink")) %\>%

layout(title = "Error Series", yaxis = list(title = "Absolut error"),
xaxis = list(title = "Date"), legend = list(x = 0.99, y = 1), hovermode
= "compare")


    ### Graph explanation:

    Most of the results are below the mean.\
    Except of the outlier, all the results has error equal/below 10 with large block of point below 5.
    As the days go by our error is small, it can happened due to that the date really gives a good prediction to concern, or if the train dataset contains larger scatter of points on these dates - check it in the next chunk.

    <br>

    **Note:** \
    Pink - median error.\
    Blue - mean error.\
    Green dots - error for sample.

    **The big difference at the first date may comes from fewer values with an early date values in the train. **
    **Check if it's true:**
    checking by compare the median days past:

    ```{r}
    median(Train$Log_Days_Past) > median(Data_For_Model$Log_Days_Past)

**Answer- no, the median days past is not greater at the train than the
test**\
So it's not relative lack of earlier values.\
We will conclude that probably the value zero(the first row) relate to
the next rows, gives this outlier. .\
**Note:**\
We tried without the log and it gives less good results, and it's
impoartant to emphasize that the corelation is not bad at all (above
8.5).\

### **Conclusion:**

*An increase in the time and amount of words that have a positive /
negative emotion (words with strong content) spoken can predict the
value of concern for that day among Democrats with mean absolute error -
below the range 5-7* (Alternates for different cross validation)
`<br>`{=html}

`<br>`{=html}

`<br>`{=html}

## **Q3**

### Formulate a meaningful question:

We chose a topic which relates to us, **grades in a schools in the
diffrent stste at United States **

### **Would the degree of education of a country indicate its ability to cope with the plague.**

**In Simple words:** Can grades be an indication of a state's ability to
minimize its number of new confirmed cases?

### Explore in the wild for a data

Here is a link for the source of the data set
"<https://www.kaggle.com/noriuk/us-education-datasets-unification-project>"\
The origin of the table is Kaggel, a site demonstrate **sharing of
wisdom of the masses** therefore we can treat the data as a reliable for
further research.
`{r echo=TRUE, message=FALSE, warning=FALSE} Education<- read_csv('data//states_all.csv')  # open file`

**Note:** We have turned off the comments issued by the chunk, because
they are only prints of the system and irrelevant

`<br>`{=html}

Checking some attributes of the data using glimpse.

``` {.{r}}
glimpse(Education)
```

**Summary:**

We can see that the Education data frame size is 1715 rows on 25
columns:

-   We can see that while first half of the columns related to revenue
    and expenses, the second half contain info about grades.

-   The table contains: 2 type of varaible:

-   dbl which relate money or grades or for the year information was
    collected.

-   chr for state name, and primary key

There are many columns with NA values after a deeper look, we understand
it related to exams which occur **every two years**,(there more explain
on them later).\
The columns related to revenue and support and expenses will not be
tough while we focus on average grade in different professions.

`<br>`{=html}

#### A quick look at the data set

``` {.{r}}
head(Education, n = 10)
```

### Explore , How grading for a state looks like?

We will focus on particular state for the observe it's grades

\`\`\`{r fig.width=9} plot_ly(data = Education %\>%
filter(STATE=="ALABAMA") %\>% na.omit()) %\>% add_trace(x = \~ YEAR, y =
\~ AVG_MATH_4\_SCORE, type = "scatter", mode = "lines+markers", name =
"Math 4 garde", hoverinfo = 'text', text =
\~paste("`</br>`{=html}Garde:", AVG_MATH_4\_SCORE,
"`</br>`{=html}Year:", YEAR), line = list(color = "hotpink"), marker =
list(color = "hotpink")) %\>% add_trace(x = \~ YEAR, y = \~
AVG_READING_4\_SCORE, type = "scatter", mode = "lines+markers", name =
"Reading 4 garde", hoverinfo = 'text', text =
\~paste("`</br>`{=html}Garde:", AVG_READING_4\_SCORE,
"`</br>`{=html}Year:", YEAR), line = list(color = "hotpink"), marker =
list(color = "hotpink")) %\>% add_trace(x = \~ YEAR, y = \~
AVG_MATH_8\_SCORE, type = "scatter", mode = "lines+markers", name =
"Math 8 garde", hoverinfo = 'text', text =
\~paste("`</br>`{=html}Garde:", AVG_MATH_8\_SCORE,
"`</br>`{=html}Year:", YEAR), line = list(color = "slateblue"), marker =
list(color = "slateblue")) %\>% add_trace(x = \~ YEAR, y = \~
AVG_READING_8\_SCORE, type = "scatter", mode = "lines+markers", name =
"Reading 8 garde", hoverinfo = 'text', text =
\~paste("`</br>`{=html}Garde:", AVG_READING_8\_SCORE,
"`</br>`{=html}Year:", YEAR), line = list(color = "slateblue"), marker =
list(color = "slateblue")) %\>%

layout(title = "Average score at math and reading exam of Alabama
state", yaxis = list(title = "Average grade", range=c(200,280)), xaxis =
list(title = "Year", range= c(2002,2016)), legend = list(x = 0.99, y =
1), hovermode = "compare")

    ### Graph explanation:

    It should be noted that the grades in 8th grades are significantly
    higher than the grades in 4th grades.\
    In addition one can see a tendency of the grades in mathematics and reading to go up
    as time passed.\ 

    The data contains information of average grade for the state every 2 years, after reading,
    Kaggel description of the table, it was mentioned, research conduct every 2 years.

    **Note:** The scale starts at 200 and end at 280, we would prefer that
    because if we initialize the score to be 0 it will be difficult to
    notice small changes, and we ignore NA values(this will cover later)

    <br>


    #### Editing the table for further work to suit for our other tables

    First we want to change the name of the column to start with capital and states name 
    letter and replace space between word with "_".
    ```{r}
    Education$STATE<-gsub(" ", "_", toTitleCase(tolower(gsub("_", " ", Education$STATE))))
    colnames(Education)<-gsub(" ", "_", toTitleCase(tolower(gsub("_", " ", colnames(Education)))))
    Education

`<br>`{=html}

#### Using countries dictionary

Please note that **adding data requires us to make some adjustments** as
for the country names, we will use the countries dictionary again to
filter corresponding state to our previous table case.\
In order to do that:

1)  Get all states name in our education data set,using unique function.

2)  We noticed **DC and the other territories** don't have records of
    their education grade so we will remove them from country vector
    before using the dictionary.

3)  Check if both length of vectors are equal.

``` {.{r}}
unique(Education$State) 
new_country_vec<-setdiff(as.vector(country[2:52]), "DC")
```

`<br>`{=html}

### Arrange our table

After clearing the data from the data set, selecting the relevant
columns for us after understanding the date set.\
It can be seen that the average calculation of each country is done
every two years and therefore in every even year the values are missing
NA so we will perform the **module** operation.\
At the previous chunk noticed that it unique state return some country
we don't have at cases table so we will use th abbrev dict to filter
them.

``` {.{r}}
dict_abbrev<-read.csv('https://bit.ly/2ToSrFv')
abbrev_to_name<- countrycode::countrycode(new_country_vec, 'abbreviation', 'state',custom_dict = dict_abbrev)
abbrev_to_name<- gsub(" ", "_", na.omit(abbrev_to_name)) #replace space with "_"

Education<- Education %>%
  select(State, Year, Avg_Math_4_Score, Avg_Math_8_Score, Avg_Reading_4_Score, Avg_Reading_8_Score)  %>% # relvent columns
  filter(State %in% abbrev_to_name)%>%
  arrange(Year)%>%
  filter(Year>=2003 & Year %% 2 !=0) # before year 2003 values are missing , preform module to get years which ar not even

Education<-append_factor(Education) #we will add new column Region with suitable values
```

`<br>`{=html}

### Exploring average reading grades at diffrent regions

\`\`\`{r fig.width=9} geom_density_math \<-ggplot(Education, aes(x =
Avg_Math_4\_Score, y = Region, fill = Region)) +
geom_density_ridges(alpha=0.6, bandwidth =1.76) + theme_ridges() +
geom_vline(data=Education, aes(xintercept=median(Avg_Math_4\_Score),
color=Region), color="red", size=0.8)+ labs( title = "Density plot
presents of the scores at math by regions", subtitle = "Sub plot for
each region", x = "Scores", y = "density")+

theme( legend.position="none", panel.spacing = unit(0.1, "lines"),
strip.text.x = element_text(size = 8))

geom_density_math


    ### Graph explanation:

    The  plot implies the difference between the median line to the position of each region by density of their scores as how much the region scroes are higher then then the median value and their number is larger we saw evaluate the educaton level at the state in the profession .\
    For example Northeast has in average a more higher grades then West and South, and more then that South.\
    South has more grades in the left side of the line which means it has more lower grads in total at reading for 4 grade.\
    From this plot we are **starting to gather a though about regions education level.**

    **Note:** The scale starts from 200 because that's the min average
    grade. we would prefer that because if we initialize the score to be 0
    it will be difficult to notice small changes.

    <br>

    ### Get average calculation for states

    We now want to calculate an average grade in each of the professions for
    each country separately.
    ```{r}
    Avg_Grading<- Education %>% 
        group_by(State, Region) %>% 
        summarise_at(vars(Avg_Math_4_Score, Avg_Math_8_Score, Avg_Reading_4_Score, Avg_Reading_8_Score), list(~ mean(., )))
    Avg_Grading

`<br>`{=html}

### Violin_plot

**Note:** The circle shows the average score at reading 8th grade for
each region \`\`\`{r fig.width=9} Avg_violin_plot\<-ggplot(Avg_Grading,
aes(x=Region, y=Avg_Reading_8\_Score, color=Region)) +
geom_violin(trim=FALSE)+ geom_jitter(shape=16,
position=position_jitter(0.1))+
scale_color_manual(values=c("cornflowerblue", "darkorange",
"darkviolet", "forestgreen"))+ stat_summary(fun=mean, geom="point",
shape=1, size=3.6, color="black")+ labs(title = "Averge score at reading
8 grade by diffrent regions", x = "Region", y = "Avg_Reading_8\_Score")
ggplotly(Avg_violin_plot)


    ### Graph explanation:

    A violin plot is a mirrored density plot, with that knowledge, we can understand that width of the graph indicates the degree of density 
    for each region at reading 8 grade. \
    Unlike the graph that presented the density for each area in mathematics here we examine the reading and calculate the average of each area individually.\
    This graph gives us a look at **the differences between the differences in scores in states**, it can be seen that the green violin shows a kind of division of the scores into two regions hence the narrowing of the violin which means maybe West region is less **"stable"** and we need to take it in account to evaluate the results better if we get a odd result from this region.\
    After that been said other regions show a clearer trend in their grades.
    The position of the violin seems to show that again the Northeast with the highest scores and Midwest is close to it.\

    **Note:** The scale don't start at 0, we would prefer that because if we
    initialize the score to be 0 it will be difficult to notice small
    changes.

    <br>


    <br>

    ### Create a new variable

    We would like to determine a **new variable by which we can assess the
    nature of a country's ability** to emerge from the crisis.\
    To this end, we will use a data set of population sample in each
    country.\

    We will use the **same data set we used at Q1**
    We would like to have a quick look at the data we will use ***head**
    ```{r}
    head(Population_Df, n = 10)

`<br>`{=html}

### Visualization of Proportion of regions

We would like to apply function to append each state the suitable region
as earlier.\
A graph showing the percentage of the U.S. population by region.
`{r fig.width=9} regional_proportion<- ggplot(data=append_factor(Population_Df) %>% filter(State %in% Avg_Grading$State)        , aes(x=Region, y= Percent_of_Total, fill= Region)) +   geom_bar(stat="identity")+   labs(   title = "Proportion of each region in relation to the United States population",   x = "Region",   y = "Propotion") regional_proportion`

### Graph explanation:

It is easy to see that in the region South has the population number is
the highest than in the rest of the regions.\
In addition to the other total percentage of population for other
regions is not so great but it is important to remember that a **single
percentage** out of the total United States is significant large then
what we think.\

#### If we are aiming to have a new variable we need to take in consideration normalize by proportion.

**Note:** The population is about 649,719,364 residents.(calculate:
sum(population\$July.2019.Estimate))

`<br>`{=html}

`<br>`{=html}

### Calculation our variable:

1)  **Difference Stage:** We would like to calculate the difference in
    the number of patients from 01/06/21 from the day the vaccines were
    given in the US 12/03/21.

2)  **Derivative Stage:** Divide the result by the number of days
    elapsed.

3)  **Normalization Stage** We will use the proportion of the population
    of each country in relation to the entire United States.\

`<br>`{=html}

### Understanding the results:

**Positive results:** indicate a poor ability of the state to deal with
the plague.

**Negative results:** indicate a good ability of the state to deal with
the plague.

### Step 1- Diffrance and Derivative Stage:

We will take the **first day they started vaccinating the population**
(12/03/21) with the help of the "Modern" and "Pfizer" vaccine and the
information that appears in the table two weeks ago (01/06/21) and we
would like to see the difference between the number of confirmed cases.\
Then divide by the number of days that have passed in order to get the
**derivation of the change.**\
Subtraction of confirmed cases (01/06/21) from (12/03/21).

``` {.{r}}
first_day<-'2021-03-12' 
last_day<-'2021-06-01'

Derivative_Cases  <- Cases %>%
  filter(Date==first_day | Date==last_day) %>% 
  select(Education$State) 

# We will keep a vector with all the patients at first day and last day
Before<- as.vector(unlist(Derivative_Cases[1,]))
After<- as.vector(unlist(Derivative_Cases[2,]))
Derivative_Cases

Derivative_Cases  <- Derivative_Cases%>% 
  mutate_all(list(~(. - lag(.)))) %>% # subtraction of the lines from each other
  mutate_all(list(~(. / as.numeric(round(difftime(last_day, first_day)))))) %>% # Divide using difftime function
  na.omit # omit NA
Derivative_Cases
```

`<br>`{=html}

### Step 2: perform a pivot longer

We would like to perform a pivot longer to turn columns into rows so we
can join different data sets population and grades scores

``` {.{r}}
#pivot table
Pivot_Derivative <-Derivative_Cases %>%
  pivot_longer(!0, names_to =c("State"), values_to = "Diff")

Pivot_Derivative<-Pivot_Derivative %>%  
  mutate(Confirmed_first_day=Before, Confirmed_last_day=After)
Pivot_Derivative
```

`<br>`{=html}

### Visualization what we done so far

A plot that shows the derivative of change at confirmed cases.`\n`{=tex}
**Note:** our new variable **is missing normalization stage** which yet
to come.

\`\`\`{r fig.width=9} Pivot_Derivative\$hover \<- with(Pivot_Derivative,
paste("State:", State, "`</br>`{=html}Confirmed first
day:",Confirmed_first_day, "`</br>`{=html}Confirmed last
day:",Confirmed_last_day))

ratio_map \<- list(scope = 'Usa', projection = list(type = 'albers
usa'), showlakes = TRUE, lakecolor = toRGB('white'))

plot_geo(Pivot_Derivative,locationmode = 'USA-states') %\>% add_trace(z
= \~Diff, text = \~hover, locations = \~state.abb\[match(gsub(\"\_","
\",Pivot_Derivative\$State),state.name)\], color=\~Diff,
colorscale="Viridis") %\>%

      colorbar(title = "Diff change") %>% 
      layout(title = "Map showing the derivative of each country's change in the confirmed cases",
      geo = ratio_map)


    ### Graph explanation:

    The scale in the graph shows the change of each country according to the
    number of patients in the country.\
    New York and Texas lead over the rest of the states in our calculation
    therefore their color is strong while the colors regions are in the
    range of green and yellow.\
    The plot **suggest** we have to do some normalization cause it is difficult to evaluate country ability's to cope with crisis without consider it's population size.\

    <br>

    ### Step 3 - Normalization Stage:

    Now we will join Pivot_derivative with Population data set.\
    We finally have our variable **Dev_Prop**

    ```{r}
    Dev_Population<- Pivot_Derivative %>%
      inner_join(Population_Df, by="State") %>%  #inner join
      mutate(Dev_Prop=(Diff/Percent_of_Total)) %>%  # divide by proportions of the population within the USA
      select(State,Dev_Prop, Percent_of_Total) # select relevant columns 

    Dev_Population

Now we can see that the highest Dev_Prop is not 109 as New_York had
earlier is now 18, all depends of it **proportion in relation to the
general population.**

`<br>`{=html}

### Step 4 - join tables

We would like to join the average grades table with the Dev_population

``` {.{r}}
Dev_Population<- Dev_Population %>% 
  inner_join(Avg_Grading, by="State")

Dev_Population
```

`<br>`{=html}

### Step 5 - Estimate which profession to focus on

Using **covariance matrix** ,we would like to find the variable that has
the highest correlation in absolute value with Dev_Prop in order to
understand the nature of their relationship we will use **cor,
sapply**.\
We going to look at the Dev_Prop column, it can be seen that the highest
is Avg_reading_4\_score, **\|-0.3228672\|**

``` {.{r}}
col <- colorRampPalette(c("#BB4444", "#EE9988", "#FFFFFF", "#77AADD", "#4477AA"))
corrplot(cor(Dev_Population[sapply(Dev_Population, is.numeric)]), method = "color", col = col(200),  
         type = "upper", order = "hclust", 
         addCoef.col = "black", # Add coefficient of correlation
         tl.col = "darkblue")
```

### Visualization of Dev_Prop

Now let's see the connection visually, for each state
\`\`\`{r,warning=FALSE,message=FALSE,fig.height==10, fig.width=10}

plot_ly(Dev_Population , y = \~Avg_Reading_4\_Score , x = \~Dev_Prop,
type = 'scatter', color = \~Region, sizes = c(7, 70), size =
\~Percent_of_Total, mode = 'markers', marker = list(sizemode =
'diameter' , opacity = 0.5), hoverinfo = 'text',

        text = ~paste("</br> State: ", State, 
                "</br> Dev_Prop: ", round(Dev_Prop,digits = 2),
                "</br> Percent of population in US: ", round(Percent_of_Total,digits = 2),
                "</br>  Average grades at reading 4 score: ",round(Avg_Reading_4_Score , digits = 2))) %>% 

      layout(shapes=list(type='line', x0=-25,x1=10,
                         y0=mean(Dev_Population$Avg_Reading_4_Score ),
                         y1=mean(Dev_Population$Avg_Reading_4_Score ),
                         line=list( width=2, color='red')),
      title = 'Comparing the Dev_Prop in relation to country average score in math',
      xaxis = list(title = "Dev_Prop", showgrid = TRUE),
      yaxis = list(title = "Avg_Reading_4_Score ", showgrid = TRUE))


    ### Graph explanation:

    Let's look at each quarter separately:\

    1)  **Quarter 1:**\
        Dev_Pop is positive and therefore the country's ability
        to get out of the crisis is low.\
        It seems that there are few state whose score is higher than the average score,
        there fore it's is hard to indicate on tenancy.\n
        
    <br>

    2) **Quarter 2:**\
        Dev_Pop is negative and therefore the country's ability
        to emerge from the crisis is high, in the quarter there are a
        **large number of countries** with an average score higher than the
        average score in the country.\
        
        **Assuming for a moment that our research question is correct**\
        We now can see that there is a connection between the education of the
        state and its ability to cope, means a smarter the country is the ability is rasing.

    <br>

    3)  **Quarter 3:**\
        Dev_Pop is negative and therefore the country's ability
        to emerge from the crisis is high.\
        There states there are imply the opposite of Quarter 2 cause there average score is lower than the
        national average, **which means contradict our Opposes our assume.**

    <br>

    4)  **Quarter 4:**\
        Dev_Pop is positive and therefore the country's ability
        to get out of the crisis is low, it seems that there are **few
        countries** with an average score lower than the overall average
        score.\
        
        **Assuming for a moment that our research question is correct**\
        Small number of state in this quarter can indicts that there is a connection between education leve, when compared to quarter 2.

    <br>
     
    **Note:**We turned off the error message `line.width` does not currently
    support multiple values.\
    After searching the internet we realized that this alert is common when
    using this type of graph and it does not hurt the correctness, because
    we trying to fit size of the circles according to too many different
    proportions.

    <br>

    All of the state of Northeast are above the red line, therefore let's have a look at their Dev_Prop.\
    **Note: It is highly recommended to jump to part 1 of the work to see the graph by each area**

    ##### Check Northeast seperatly

    ```{r}
    temp<-Dev_Population %>% filter(Region=="Northeast")
    corrplot(cor(temp[sapply(temp, is.numeric)]), method = "color", col = col(200),  
             type = "upper", order = "hclust", 
             addCoef.col = "black", # Add coefficient of correlation
             tl.col = "darkblue")

A look at Northeast separably imply that maybe the link is not as clear
as we thought before.\
Avg_Reading_4\_Score with Dev_Prop is 0.04 means it is close to zero,
which implay that the correlation is missing, **not as we hoped.**\
We will focus on all the states at US and not on a separate region,
**for understanding the bigger picture.** `<br>`{=html}

### Exploring our variable nature

Now we want to check out our meaningful question.\
We will use linear model to test whether there is a relationship between
a country's ability to deal with an epidemic according to the our
variable we created in relation to its average grade in mathematics.\

\`\`\`{r fig.width=9} lin_reg\<-ggplot(Dev_Population, aes(x =
Avg_Reading_4\_Score , y = Dev_Prop)) + geom_point() +
geom_smooth(formula =y \~ x, method = "lm", col = "blue")

main_sign\<-
signif(coef(lm(Dev_Population$Dev_Prop ~ (Dev_Population$Avg_Reading_4\_Score
)))) main_equ\<-paste("Equation:", "y=", round(main_sign\[1\],2), "+",
round(main_sign\[2\],2),"x") main_cor\<-paste(\" , Correlation :",
round(cor(Dev_Population$Dev_Prop, Dev_Population$Avg_Reading_4\_Score ,
method ="pearson\"),digits=3)) main_title\<-paste('`<b>`{=html}lm:
Avg_Reading_4\_Score `</b>`{=html}','`<br>`{=html}',main_equ, main_cor
,'`</sup>`{=html}')

ggplotly(lin_reg, tooltip = "text") %\>% layout(title =
main_title,margin = list(t = 75))


    ### Graph explanation:

    A quick look:\
    It can be seen that there is a tendency of the grade scores to go up
    with the ability of our variable, by the line lm created.\
    **But is this really the truth?**\
    A deeper look:\
    It can be seen that the line does not accurately goes on most of the points, and there is a big difference between some points which can be explain the cor value.\
    Some of the points the line didn't pass on them are those with positive Dev_Prop, with indicates as we are in the right way to, **but can we get a better fit and correlation.**
    <br>

    ### Even a deeper look:

    We would like to see the tendency of each region separately.

    ```{r fig.width=9}
    ggplotly(ggplot(Dev_Population, aes(x = Avg_Reading_4_Score, y = Dev_Prop)) +
        geom_point() + 
        geom_smooth(formula =y ~ x, method = "lm", col = "blue") +
        facet_wrap(~ Region) +
        labs(title = "lm: graphs present tendency of diffrent regions"))

### Graph explanation:

1)  **Midwest:** Tendency to go down, many point are in the era of the
    lour line which imply that the lm fit a good result at this region.

2)  **South:** Tendency is to go up, it's still negative value at
    Dev_Prop but the tendency imply a connection from a different angle.

3)  **Northeast:** The line remains balanced while passing at points.

4)  **West:** There is a tendency to rise. more tan that the Dev_Prop
    value is close to zero means it is oppose the tendency of Midwest
    region.

This explains the results we saw in the previous graph when summing it
all up the variable shows a small tendency to go down but not
significantly so **things balance out to one line.**\

Therefore it can be said that it is difficult to see a clear trend.\

`<br>`{=html}

### Model with multiple predictors

We would like to see if we can build a better linear model by appending
one more variable.\
We will use tidy to see see the model properties

``` {.{r}}
# Main model we worked the model use grades at math in 4th grade
Main_Model<-linear_reg() %>%
  set_engine("lm") %>%
  fit(Dev_Prop ~Avg_Reading_4_Score, data=Dev_Population)
tidy(Main_Model)

# Temp model with multiple predictor, the model use the grades at reading
Temp_Model <- linear_reg() %>%
  set_engine("lm") %>%
  fit(Dev_Prop ~ Avg_Reading_4_Score + Avg_Math_8_Score    , data = Dev_Population)
tidy(Temp_Model)
```

`<br>`{=html}

### Put all in one table

Checking the quality of the model We will use glance function to how
much the r.squared and adj.r.squared are different.

``` {.{r}}
Two_Modle_Glance<-rbind(cbind(Mod = "Main_Model", glance(Main_Model)),cbind(Mod = "Temp_Model", glance(Temp_Model)))
Two_Modle_Glance
```

**In terms of :**

-   **P value:** Temp_Model significance of the model decreased as we
    chose alpha to be 5%, compare to Main_Model with much lower p value
    lower then 5%.

-   **Sigma:** The variance has not changed so we will not be able to
    expand more on it.

`<br>`{=html}

#### Check if the temp model has better r.squared:

``` {.{r}}
glance(Temp_Model)$r.squared>glance(Main_Model)$r.squared
```

-   **R Squared:** Temp_Model change is not so great even though it has
    risen, it limit our assessment to say that Temp_Model is better then
    Main_Model.

`<br>`{=html}

#### Check if the temp model has better Adj.r.squared:

``` {.{r}}
glance(Temp_Model)$adj.r.squared>glance(Main_Model)$adj.r.squared
```

-   **Adj.R.Squared:** Temp_Model there is a decrease at the value so in
    this term Temp_Model is not better then Main_Model.

#### Conclude:

We understand that the changes are not add up in any of the metrics so
we can say that adjusting the model by adding another variable **didn't
not help us improve the quality of the model**

`<br>`{=html}

### Two lm plots together

We now want to see the model we created visually to see if the
correlation has changed and if the llm line is able to better predict
and pass more points.

\`\`\`{r, fig.width=14}

temp_sign\<-
signif(coef(lm(Dev_Population$Dev_Prop ~ (Dev_Population$Avg_Reading_4\_Score+Dev_Population$Avg_Math_8_Score )))) temp_equ<-paste("Equation: ", "y= ", round(temp_sign[1],2), "+", round(temp_sign[2]* temp_sign[3],2),"x") temp_cor<-paste(" , Correlation :", round(cor(Dev_Population$Dev_Prop,
Dev_Population$Avg_Reading_4_Score+Dev_Population$Avg_Math_8\_Score ,
method = "pearson"),digits=3)) temp_title\<-paste('`<b>`{=html}lm: Avg
math+Reading 4 grade and Dev_Prop
`</b>`{=html}','`<br>`{=html}',temp_equ, temp_cor , '`</sup>`{=html}')

lin_reg_Main\<-ggplotly(ggplot(Dev_Population%\>% mutate(Sub_title =
temp_title) , aes(x = Avg_Reading_4\_Score+Avg_Math_8\_Score, y =
Dev_Prop))+ facet_wrap(\~Sub_title) + geom_point(alpha=0.7) +
geom_smooth(formula =y \~ x, method = "lm", col = "orange"))

lin_reg_Temp\<-ggplotly(ggplot(Dev_Population%\>% mutate(Sub_title =
main_title) , aes(x = Avg_Reading_4\_Score, y = Dev_Prop))+
facet_wrap(\~Sub_title) + geom_point(alpha=0.7) + geom_smooth(formula =y
\~ x, method = "lm", col = "blue"))

subplot(lin_reg_Main,lin_reg_Temp) \#present both plot together at the
same row

\`\`\`

### Graph explanation:

It can be seen a change in the correlation by an absolute value that has
decreased from **\|(-0.323)\|** to **\|(-0.318)\|**, **as we expected**
when we saw that we noticed **no change for the better** in the measures
in terms of R squared and Adj.r.squared, p value and etc.\

Although we tried to raise in absolute value the correlation by **many
combinations** , we got is still the best value is be reading 4 grade.\

**Note:** The scale starts not at zero, we would prefer that because if
we initialize the score to be 0 it will be difficult to notice small

### **From bottom to top**

We will briefly summarize what we have done so far:\

1)  **Formulate a meaningful question**

2)  **Exploration:**\
    Understanding the data set contains the scores in the states in the
    United States and visual it.\

3)  **Creating a variable:**\
    By calculating the change of each country individually in relation
    to its proportion, we were able to determine the nature of a state's
    ability.\

4)  **Modeling of the Variable Impact:**\
    We wanted to choose from the basket of variables we have the
    variable that can be most influential.\

5)  **Model Quality Assessments:**\
    We compared the model we created against another model with more
    variables.\

6)  **Conclusions:** In our estimation, there is a relationship between
    the average score at 4 grade, and the ability of a country to emerge
    from the crisis, although the relationship is not strong as we
    wished for (correlation is not high enough in our estimation).\
    While we have seen that dividing for each region separately balances
    the results of a tendency to decrease to a low value of the
    Dev_Prop, we have the suspicion that we need to consider whether we
    want to test whether there is a relationship in each region
    separately.\
    Because our research question looked at **spatial vision** we did
    not delve into the subject but it is important to note this for
    future study.\
    **For those reasons we say that grades are not an unequivocally that
    the grades can be an indicator.**

7)  **Recommendation:** Our recommendations for further research may be
    to focus on **additional columns that appear in the table** such as
    financial support and revenue, perhaps they can improve our
    results.  We would suggest taking into account data collected for
    older age groups, as these are **more prone to illness than children
    in school**, perhaps an academic average of students, or a **status
    eligible for a master's or doctoral degree that may indicate a trend
    more significant** than school grade.

`<br>`{=html}

## **-------THE END-------**
