#
# EIS Policy / Customer generator
#

import os, sys, argparse, json, random, time, tqdm
from jinja2 import Environment, FileSystemLoader
from progressbar import Bar, Percentage, ProgressBar

def main():

    parser = argparse.ArgumentParser(description=
        'EIS policy/customer generator. By default generates customers (customer.count) \
        with number of policies (policy.count) for each one (see configuration file)'
    )

    parser.add_argument("--config", help = 'configuration file', default = 'generator.conf.json')
    parser.add_argument("--output", help = "output dir", default = 'output')
    parser.add_argument("--only_customers", help = "generate only customers", action='store_true')
    parser.add_argument("--only_policies", help = "generate only policies", action='store_true')

    args = parser.parse_args()

    output_dir_customer = args.output + '/customers'
    output_dir_policy = args.output + '/policies'

    check_output_dir(output_dir_customer)
    check_output_dir(output_dir_policy)

    config = read_config(args.config)
    config_customer = config['customer']
    config_policy = config['policy']

    printInfo(args)

    j2_env = Environment(loader = FileSystemLoader(''), trim_blocks = True)
    customer_template = j2_env.get_template(config_customer['template'])
    policy_template = j2_env.get_template(config_policy['template'])

    if not args.only_policies:
        # generating customers

        customer_start = config_customer['start']
        customer_count = config_customer['count']
        policy_start = config_policy['start']
        policy_count = config_policy['count']

        pbar_customers = ProgressBar(widgets=['Generating customers: ', Percentage(), Bar()], maxval=customer_count).start()

        for customer_num in range (customer_start, customer_start + customer_count):
            write_file(
                output_dir_customer + "/customer_" + str(customer_num) + ".xml",
                generate_customer(config_customer, customer_num, customer_template)
            )
            pbar_customers.update((customer_num - customer_start) + 1)

            if not args.only_customers:
                # and policies for every customer

                pbar_policies = ProgressBar(widgets=['Generating policies for ' + str(customer_num) + ': ', Percentage(), Bar()], maxval=policy_count).start()

                for policy_num in range(policy_start, policy_start + policy_count):
                    write_file(
                        output_dir_policy + "/policy_" + str(policy_num) + ".xml",
                        generate_policy(config_policy, customer_num, policy_num, policy_template)
                    )
                    pbar_policies.update((policy_num - policy_start) + 1)
                pbar_policies.finish()
                
                policy_start = policy_start + policy_count

        pbar_customers.finish()
    else:
        # generating only policies

        policy_start = config_policy['start']
        policy_count = config_policy['count']



        pbar_policies = ProgressBar(widgets=['Generating policies: ', Percentage(), Bar()], maxval=policy_count).start()

        for policy_num in range (policy_start, policy_start + policy_count):
            write_file(
                output_dir_policy + "/policy_" + str(policy_num) + ".xml",
                generate_policy(config_policy, config_policy['customerNumber'], policy_num, policy_template)
            )
            pbar_policies.update((policy_num - policy_start) + 1)
        pbar_policies.finish()

def printInfo(args):
    print('------------------------------------------------------')
    print('Config file:\t\t\t' + os.path.abspath(args.config))
    print('Output folder:\t\t\t' + os.path.abspath(args.output))
    print('------------------------------------------------------')


def generate_customer(config, customer_num, customer_template):
    return customer_template.render(
        customer_number =   customer_num,
        address_line_1 =    create_uniq_prop_with_suffix(config['streetNames'], 4),
        address_line_2 =    create_uniq_prop_with_suffix(config['areaNames'], 4),
        address_line_3 =    create_uniq_prop_with_suffix(config['placeNames'], 4),
        city =              create_uniq_prop(config['cityNames']),
        country_cd =        create_uniq_prop(config['countryCodes']),
        postal_code =       create_uniq_number(5),
        email_id =          create_uniq_prop_with_suffix(config['firstNames'], 4) + '@email.com',
        phone_number =      create_uniq_number(7),
        first_name =        create_uniq_prop_with_suffix(config['firstNames'], 4),
        last_name =         create_uniq_prop_with_suffix(config['lastNames'], 4),
        middle_name =       create_uniq_prop_with_suffix(config['firstNames'], 4),
        birthdate =         config['birthdate'],
        gender_cd =         create_uniq_prop(config['genderCd']),
        title_cd =          create_uniq_prop(config['titleCd']),
        source_reference =  customer_num - 2,
        producer_cd =       config['producerCd']
    )

def generate_policy(config, customer_num, policy_num, policy_template):
    return policy_template.render(
        customer_number =   customer_num,
        effective_date =    config['effectiveDate'],
        expiration_date =   config['expirationDate'],
        policy_number =     config['policyNumberPrefix'] + str(policy_num),
        producer_cd =       config['producerCd'],
        product_cd =        config['productCd'],
        due_day =           config['dueDay'],
        enable_recurring_payments = config['enableRecurringPayments'],
        payment_plan =      config['paymentPlan'],
        cost_of_purchase =  create_uniq_number(4),
        present_value_amt = create_uniq_number(4)
    )

def create_uniq_prop_with_suffix(property_value, suffix_len):
    value = create_uniq_prop(property_value)
    suffix = create_uniq_number(suffix_len)
    return value + str(suffix)

def create_uniq_prop(property_value):
    name = random.choice(property_value)
    return name

def create_uniq_number(digits):
    lower = 10**(digits - 1)
    upper = 10**digits - 1
    return random.randint(lower, upper)

def check_output_dir(path):
    if not os.path.exists(path): os.makedirs(path)

def read_config(path):
    return json.load(open(path))

def write_file(filename, data):
    with open(filename, "w") as f:
        f.write(data)

if __name__ == "__main__":
    main()
