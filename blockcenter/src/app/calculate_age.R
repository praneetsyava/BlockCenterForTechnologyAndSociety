# calculate_age.R

calculate_age_and_day_of_birth <- function(dob) {
    dob <- as.Date(dob, format="%Y-%m-%d")
    age <- as.numeric(difftime(Sys.Date(), dob, units="days")) %/% 365
    day_of_week <- weekdays(dob)
    list(age=age, day_of_week=day_of_week)
}
