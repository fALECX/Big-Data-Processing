visits = load 'hdfs:///visits' using PigStorage(',') as (user, url, time);
gVisits = group visits by url;
visitCounts = foreach gVisits generate group as url, COUNT(visits) as count;
urlInfo = load 'hdfs:///urlInfo' using PigStorage(',') as (url, category, pRank);
joinInfo = join visitCounts by url, urlInfo by url;
gCategories = group joinInfo by category;
topUrls = foreach gCategories generate TOP(2,1,joinInfo);
store topUrls into 'hdfs:///topUrls';


