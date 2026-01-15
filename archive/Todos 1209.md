perform the below todos
    Create a full backup in zip file of the entire project
    clean up the unused files, back them up in an Archive dir
    Rearrange the files if possible to a better dir structure (clearly separate the desktop version vs the mobile app
    Perform a functional test after all this is done
    If all tests are successful create a 2nd backup file in zip of the entire project
    Then start to perform the next functional changes or extensions. Ensure no existing, working functions are ruined! So before deep changes ensure dependencies are checked. Every working functional change should be also documented in the 2nd instructions.md file
    Ensure first you understand the entire todo list below, if there are clarifications, first ask them and then perform one by one, ensuring no ruining prior working versions
    In the portable desktop version
        in the dashboard, the graph Asset breakdown should also present actual values in HUF, not only %
        in Analytical Data, in Portfolio Summary Over Time I miss Loan/Liabilities (as minus)
        in Analytical Data we need to add a detailed table for All Portfolio Items and Wealth items in HUF, over time - the same structure as in Portfolio Summary Over Time
        in Analytical Data when granularity is changed to monthly, nothing is changed in the view. it should only show the value for the first date of each month (now only december exists, but later for new records there will be first records in a month). or the closest snapshot to the 1st day of the month, or after
        In Wealth management we should add some automatic calculations to some of the existing line items, that should be prformed on the 1st of each months: Reduce the existing Loan according to this:
        Hitel??llom??ny CIB, Peterdy: 236667 HUF less
        Kawasaki k??telezetts??g: 40000 HUF less 
        Cabrio k??telezetts??g: 118958 HUF
        Reduce also the amount on Tartoz??s fel??m by 40000 HUF monthly (first daqy or closes to that when the app is run)
        On Portfolio & Wealth Analyzer in the graphs add data point values (arranged approx 45% turned, so that the numbers are not covering each other)

    In the mobile app version
        For NET wealth I see different amount than in the desktop version for the same date (9th Dec). Validate that supabase has the right data updated and not only some data is refreshed locally on Desktop (e.g. Pension Fund info, Snapshots)
        In Portfolio Management, on Manual Price override, the new price is saved somewhere but it is not refreshed back in Supabase, when checked in Desktop version. It needs to be checked and corrected
        In Wealth tab, the currency for the instruments is shown "null", need to check and correct
        In Trends tab the first graph, Portfolio over time has wrong numbers on the vertical axis (all is 79M) it needs to be 0 - as needed. 
        Both graphs should be able to be magnified into for better visibility
        When month view is changed to 3M or 6M or 1Y or All, nothing is changed. It should impact the view!
        Analaytics screen data tables should be resizable for better visibility. magnify, and smallify with two fingers move. Rearrange tabs: Portfolio, Wealth and then Summarize

    Analyze #history.csv that includes historical data for the different line items. This should be added as a separate DB and pulled in when analyzing trends and historical data (as monthly data). Portfolio is signed in the first column as "long" the other relate to wealth. Find their pairs if possible, bring the values on the same line item as it presently occurs in Supabase, if no match if found add them as historical portfolio or wealth items. They should not be modifiable, they should be only viewable data. They should be added to all screens where Analytical or historical data occurs both on Desktop and Mobile app
