perform the below todos
    1. clean up the unused files, back them up in an Archive dir
    2. Then start to perform the next functional changes or extensions. Ensure no existing, working functions are ruined! So before deep changes ensure dependencies are checked. Every working functional change should be also documented in the 2nd instructions.md file
    3. Ensure first you understand the entire todo list below, if there are clarifications, first ask them and then perform one by one, ensuring no ruining prior working versions
    4. In the portable desktop version
        a. in the dashboard, check Erste Bond Dollar Corporate USD R01 VTA price. it shows manual adjustment and check if it is properly updated daily when the update function is triggered
        b. remove the Snapshot data for 2025.12.03 as that looks missing some of the needed data and confuses graphs. We were at that time testing and we created this snapshot wrongly.
        c. On Portfolio & Wealth Analyzer tab under the table: Portfolio Summary Over Time add another table, with the same line items as in Portfolio Summary Over Time, the new table called: Summary Analytics. In % you should calculate the line item growth year on year to the last record (if there exists more record for a month, us the latest record for that month both for baseline and for actual). I need to see changes in % over 1 year rolling. Including the total line as well.
        d. I need another table below showing a year on year % change to all the years in the cloumns since 2015 with the prior year December as baseline with the same line items. Name should be "Summary Analytics YoY"
        e. The granualrity for the records in this tab should be also changeable to "yearly" - showing the last december data for each year
        f. I need the same two tables as described above (c. and d) below Portfolio Detail by Instrument table, applying that to Portfolio Detail by Instrument items to show YoY % change over time by Instruments. name Should be "Summary Analytics for Portfolio" and "Summary Analytics YoY Portfolio"
        g. The same two tables below Wealth Detail by Category; new table names: "Summary Analytics for Wealth" and "Summary Analytics YoY Wealth"


    5. In the mobile app version
        a. The same should be implemented in the mobile app as above in 4.c.d.f.g on the Trends tab and The Analytical Data tab. this also means the same Tables need to be created according to the Desktop app, same structure, order but graphs is OK on Trends, but the tables with data on the Analytical Data Tab
        b. In the Trends tab the graph vertical should show years as well, with text turned Vertical for visibility (year and month)
        c. In the Analytical Data tab the tables should be able to be smallified, magnified using the two fingers approach. Also make the Data Points, Instruments, Granularity information much smaller to free up screen. Make also the top Start Date and End date and Granularity selectors, and the Load Data button much smaller to fit in one Line
    6. Help me Test all new functions and features by starting the Portable Desktop application triggered from terminal or the mobile app in chrome relatively as required   (start_portable.bat and command line lunch for chrome as usual)

