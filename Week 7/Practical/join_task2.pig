visits = load 'hdfs:///visits' using PigStorage(',') as (user, url, time);
gVisits = group visits by url;
visitCounts = foreach gVisits generate group as url, COUNT(visits) as count;
urlInfo = load 'hdfs:///urlInfo' using PigStorage(',') as (url, category, pRank);
joinInfo = join visitCounts by url, urlInfo by url;
joinInfoOutput = foreach joinInfo generate visitCounts::url, urlInfo::category, urlInfo::pRank;
store joinInfoOutput into 'hdfs:///topUrls1';
