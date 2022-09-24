# tax wedge charter plotter

# (c) Dan Neidle of Tax Policy Associates Ltd
# licensed under the GNU General Public License, version 2

import plotly.graph_objects as go
import pandas as pd
from PIL import Image
# also requires kaleido package

income_multiples = [5, 20, 100]

for max_income_multiple in income_multiples:
    y_axis_ticks = max_income_multiple / 10
    income_resolution = max_income_multiple / 100  # the steps we go up

    # these are the countries visible by default; others can be turned on/off by clicking the legend
    visible_countries = "UK - old UK - after mini Budget United States France Ireland Spain Estonia Sweden Italy"

    excel_file = "personal-taxes_worldwide_data.xlsx"

    logo_jpg = Image.open("logo_full_white_on_blue.jpg")

    # returns cell value or zero if blank
    def read_cell(df, row, column):
        if pd.isna(df.iat[row, column]):
            return 0
        else:
            return df.iat[row, column]

    # create plotly graph object
    # layout settings

    logo_layout = [dict(
            source=logo_jpg,
            xref="paper", yref="paper",
            x=1, y=1.03,
            sizex=0.1, sizey=0.1,
            xanchor="right", yanchor="bottom"
        )]

    layout = go.Layout(
        images=logo_layout,
        title=f"Gross wage (as multiple of average earnings, up to {max_income_multiple}x) vs effective income tax/SS/NICs rate",
        xaxis=dict(
            title="Gross wage (multiple of average earnings)",
            dtick = y_axis_ticks
        ),
        yaxis=dict(
            title="Effective tax rate",
            tickformat=',.0%',  # so we get nice percentages
        ) )

    fig = go.Figure(layout=layout)



    print(f"Opening {excel_file}")
    xl = pd.ExcelFile(excel_file)
    print("")
    print(f"Opened spreadsheet. Sheets: {xl.sheet_names}")

    print("")

    df = xl.parse("data")

    for country_row in range (0,len(df)):
        country_name = df.iat[country_row, 0]
        average_salary = df.iat[country_row, 1]

        print("")
        print(f"Country: {country_name}, average salary {average_salary}")

        x_data = []  # income multiple
        y_data = []  # effective rate

    #   start with central income tax
        central_allowance = read_cell(df, country_row, 2)
        central_allowance_removal_threshold = read_cell(df, country_row, 101)
        central_allowance_removal_taper = read_cell(df, country_row, 102) / 100
        central_tax_credit = read_cell(df, country_row, 3)
        central_surtax = read_cell(df, country_row, 4) / 100
        central_bands = []

        for band in range (0,19):
            rate = read_cell(df, country_row, band * 2 + 5) / 100
            if pd.isna(df.iat[country_row, band * 2 + 6]):  # we reached a blank cell
                central_bands.append({"threshold": 1000000000, "rate": rate})  # code is easier if we make all bands have a threshold
                break
            else:
                threshold = df.iat[country_row, band * 2 + 6]
                central_bands.append({"threshold": threshold, "rate": rate})


        print(f"Personal allowance {central_allowance}, central credit {central_tax_credit}, surtax {central_surtax}, bands: {central_bands}")

    #   then regional etc income tax
        sub_allowance = read_cell(df, country_row, 43)
        sub_bands = []

        if not pd.isna(df.iat[country_row, 44]):
            # this country has a non-progressive sub income tax rate system
            sub_bands.append({"threshold": 1000000000, "rate": df.iat[country_row, 44] / 100})
        else:
            # this country has progressive sub rates
            for band in range(0, 12):
                rate = read_cell(df, country_row, band * 2 + 45) / 100
                if pd.isna(df.iat[country_row, band * 2 + 46]):  # we reached a blank cell
                    sub_bands.append(
                        {"threshold": 1000000000, "rate": rate})  # code is easier if we make all bands have a threshold
                    break
                else:
                    threshold = df.iat[country_row, band * 2 + 46]
                    sub_bands.append({"threshold": threshold, "rate": rate})


        print(f"Sub allowance {sub_allowance}, bands: {sub_bands}")



    #   then employer SS/NICs
        if pd.isna(df.iat[country_row, 71]):
            # this country has no employer NICs
            employer_SS_fraction = 0
        else:
            employer_SS_fraction = df.iat[country_row, 71]

        employer_lump = read_cell(df, country_row, 72)
        employer_SS_bands = []

        for band in range(0, 4):
            if pd.isna(df.iat[country_row, band * 3 + 73]):
                # we're done with employer SS
                break

            rate = read_cell(df, country_row, band * 3 + 73) / 100

            if pd.isna(df.iat[country_row, band * 3 + 75]):  # we reached a blank cell
                employer_SS_bands.append(
                    {"upper": 1000000000, "lower": df.iat[country_row, band * 3 + 74] * employer_SS_fraction, "rate": rate})  # code is easier if we make all bands have a threshold
                break
            else:
                employer_SS_bands.append(
                    {"upper": df.iat[country_row, band * 3 + 75] * employer_SS_fraction, "lower": df.iat[country_row, band * 3 + 74] * employer_SS_fraction,
                     "rate": rate})  # code is easier if we make all bands have a threshold

        print(f"Employer lump sum {employer_lump}, bands {employer_SS_bands} (all adjusted for fraction {employer_SS_fraction})")


        #   finally employee SS/NICs
        if pd.isna(df.iat[country_row, 85]):
            # this country has no employee NICs
            employee_SS_fraction = 0
        else:
            employee_SS_fraction = df.iat[country_row, 85]

        employee_SS_bands = []

        for band in range(0, 5):
            if pd.isna(df.iat[country_row, band * 3 + 86]):
                # we're done with employee SS
                break

            rate = read_cell(df, country_row, band * 3 + 86) / 100

            if pd.isna(df.iat[country_row, band * 3 + 88]):  # we reached a blank cell
                employee_SS_bands.append(
                    {"upper": 1000000000, "lower": df.iat[country_row, band * 3 + 87] * employee_SS_fraction,
                     "rate": rate})  # code is easier if we make all bands have a threshold
                break
            else:
                employee_SS_bands.append(
                    {"upper": df.iat[country_row, band * 3 + 88] * employee_SS_fraction, "lower": df.iat[country_row, band * 3 + 87] * employee_SS_fraction,
                     "rate": rate})  # code is easier if we make all bands have a threshold

        print(f"Employee bands {employee_SS_bands} (all adjusted for fraction {employee_SS_fraction})")

        # now do calcs
        for salary_multiple in [salary_multiple * income_resolution for salary_multiple in range(0, int(max_income_multiple / income_resolution) + 1)]:

            if salary_multiple < 0.1:
                # don't calculate ETFs for small salaries as lump sum SS results in unrepresentatively high ETFs
                continue

            #BELGIUM local income tax taxable income is gross of tax credits. flag should be "gross"


            salary = salary_multiple * average_salary
            total_tax = 0

            # start with employer SS

            employer_SS = employer_lump
            for x in range(len(employer_SS_bands)):

                # if below lower threshold we're done looping bands
                if salary < employer_SS_bands[x]["lower"]:
                    break

                # if we hit the next threshold then apply tax to whole band
                if salary >= employer_SS_bands[x]["upper"]:
                    employer_SS += employer_SS_bands[x]["rate"] * (
                                employer_SS_bands[x]["upper"] - employer_SS_bands[x]["lower"])  # we reach the next threshold!

                # otherwise apply tax to what's left in this band, then stop looping bands
                else:
                    employer_SS += employer_SS_bands[x]["rate"] * (salary - employer_SS_bands[x]["lower"])
                    break

            overall_wage_bill = salary + employer_SS  # we calculate ETF using this, as economic incidence is on employee
            total_tax += employer_SS

            # then employee SS

            employee_SS = 0
            for x in range(len(employee_SS_bands)):

                # if below lower threshold we're done looping bands
                if salary < employee_SS_bands[x]["lower"]:
                    break

                # if we hit the next threshold then apply tax to whole band
                if salary >= employee_SS_bands[x]["upper"]:
                    employee_SS += employee_SS_bands[x]["rate"] * (
                                employee_SS_bands[x]["upper"] - employee_SS_bands[x]["lower"])  # we reach the next threshold!

                # otherwise apply tax to what's left in this band, then stop looping bands
                else:
                    employee_SS += employee_SS_bands[x]["rate"] * (salary - employee_SS_bands[x]["lower"])
                    break

            total_tax += employee_SS



            # now central income tax

            # deal with tapered removal of personal allowance. UK only?
            if central_allowance_removal_threshold != 0 and salary > central_allowance_removal_threshold:
                reduction = salary - (central_allowance_removal_threshold * central_allowance_removal_taper)
                adjusted_central_allowance = max (0, central_allowance - reduction)
                print(f"salary {salary}, reduction {reduction}, so allowance {adjusted_central_allowance}")
            else:
                adjusted_central_allowance = central_allowance

            net_salary = max (0, salary - adjusted_central_allowance - central_tax_credit)
            central_IT = 0
            for x in range(len(central_bands)):

                if x == 0:
                    previous_threshold = 0
                else:
                    previous_threshold = central_bands[x-1]["threshold"]

                # if we hit the threshold then apply tax to whole band, less last band (if there was one)
                if net_salary >= central_bands[x]["threshold"]:
                    central_IT += central_bands[x]["rate"] * (central_bands[x]["threshold"] - previous_threshold)  # we reach the next threshold!

                # otherwise apply tax to what's left in this band, then stop looping bands
                else:
                    central_IT += central_bands[x]["rate"] * (net_salary - previous_threshold)
                    break

            central_IT += net_salary * central_surtax

            total_tax += central_IT




            # now sub income tax

            net_salary = max (0, salary - sub_allowance)
            sub_IT = 0
            for x in range(len(sub_bands)):

                if x == 0:
                    previous_threshold = 0
                else:
                    previous_threshold = sub_bands[x-1]["threshold"]

                # if we hit the threshold then apply tax to whole band, less last band (if there was one)
                if net_salary >= sub_bands[x]["threshold"]:
                    sub_IT += sub_bands[x]["rate"] * (sub_bands[x]["threshold"] - previous_threshold)  # we reach the next threshold!

                # otherwise apply tax to what's left in this band, then stop looping bands
                else:
                    sub_IT += sub_bands[x]["rate"] * (net_salary - previous_threshold)
                    break

            total_tax += sub_IT

            if overall_wage_bill == 0:
                ETR = 0
            else:
                ETR = total_tax / overall_wage_bill

            print(f"At salary {salary}, ETF {round(ETR * 100, 1)}% - employer SS is {employer_SS}, employee SS is {employee_SS}, central IT is {central_IT}, sub IT is {sub_IT}")

            x_data.append(salary_multiple)
            y_data.append(ETR)

        # add label to last data item showing country (bit hacky; must be better way)
        labels = [""] * (int(max_income_multiple / income_resolution) - 1)
        labels.append(country_name)

        if country_name in visible_countries:
            visibility = True
        else:
            visibility = 'legendonly'

        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode="lines+text",    # no markers
            name=country_name,
            text=labels,
            textposition="top center",
            showlegend=True,
            visible=visibility
        ))

    fig.show()
    fig.write_image(f"OECD_personal_{max_income_multiple}x.svg")
