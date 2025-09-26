import re

def clean_email_list(input_file, output_file):
    # Regular expression pattern for matching email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Set to store unique emails
    seen_emails = set()
    # List to store lines we want to keep
    lines_to_keep = []
    
    # Read the input file
    with open(input_file, 'r') as f:
        for line in f:
            # Find all emails in the line
            emails = re.findall(email_pattern, line)
            
            # If no email found in line, skip it
            if not emails:
                continue
                
            # Get the first email in the line
            current_email = emails[0]
            
            # If email hasn't been seen before, keep the line
            if current_email not in seen_emails:
                seen_emails.add(current_email)
                lines_to_keep.append(line.strip())
    
    # Write unique lines to output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines_to_keep))
        f.write('\n')  # Add final newline

    return len(seen_emails)  # Return number of unique emails

# Usage example
if __name__ == "__main__":
    input_file = "/Users/jmora/med/amcat/amcat_correos.txt"  # Replace with your input file name
    output_file = "cleaned_emails.txt"  # Replace with desired output file name
    
    unique_count = clean_email_list(input_file, output_file)
    print(f"Process completed. Found {unique_count} unique emails.")
    print(f"Results saved to {output_file}")