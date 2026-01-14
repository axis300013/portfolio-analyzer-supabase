This file contains additional functions to build for additional wealth vaulation
It should be structured so that it has the following data entries
I need to extend it with additional functions to evaluate entire wealth on a monthly basis.
the line items should be (Type of wealth, Name, Currency)
cash	MKB account EUR 
cash	MKB account HUF 
cash	CIB account HUF
cash	Cash at home HUF	 
cash	Revolut Account HUF	 
cash	Cash at home EUR 
cash	SZÉP Kártya HUF
Property	Peterdy 29 HUF 
Pension	Self Fund HUF	 
Pension	Voluntary Fund HUF 
Cash	Tartozás felém HUF
Loan	Hitelállomány CIB, Peterdy HUF	  
Property	motor Kawasaki HUF
Property	BMW Cabrio HUF
Loan	Kawasaki kötelezettség HUF 
Property	Szokolya HUF
Loan	Cabrio kötelezettség HUF 

Create an additional database for these
extend these with 2 more fields: Present value, Note
Add these as a separate table to the Portfolio Valuation, add the ability to manually change any record and manually add Present value to each record. Add a Total to it; and add these together into a total with the Portfolio Valuation.
Ensure all this is regressively tested throughout the entire project that was already created