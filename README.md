# exchange_tax_parsers
Collection of python scripts for pulling trades from crypto exchanges and putting in csv format for tax websites

PLEASE NOTE FOR KUCOIN:
If you have more than 100 trades, the API script does not work to retrieve them all right now (working to see if this is fixable). 
In the meantime, I've added a kucoin_parser_selenium.py script that uses selenium/chromedriver to open an instance of chrome and go thru to grab the trades.

Update: Sounds like even the selenium/chromedriver script isnt working for > 100 trades. I have heard of one work around - pull your trades for a specific trading pair as there is no page limit but I believe you can only pull 20 at a time.. So it would work to pull all of your trades if you looped over each pair, but very slow. Anyway, check the kucoin api docs if you're interested in modifying the script to do this.

Instructions are included at the top of each script, please read! Thanks!


