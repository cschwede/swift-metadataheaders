# Extract required entries from syslog, with target container and date string as first two fields
awk -F " " '/X-Container-Metadata-Log-To/ {print $20" "$8" "$6" "$9" "$10" "$12" "$17" "$18 > "unsorted"}' /var/log/syslog

# Now sort this file to make it easier for awk in the next step. This avoids heavy file seeking; otherwise every line 
# would most likely put into a different file in the next step. GNU sort is extremely fast, sorting a logfile of a few 
# hundred MB within seconds (on a Core i5 with an SSD)
sort -t " " -k 1,2 unsorted -o sorted

# Slit the logfile into single files for each target account-container pair. 
# The filename format is like 29Dec2013185541_AUTH_accountname_containername_log, making it easy
# to use in combination with swift --storage_url to upload to the target container
awk -F " " '
    NR == 1 {
        split($1, target, ":%20");
        split($5, account, "/");
        date = gensub("/", "", "g", $2);
        filename=""date"_"account[3]"_"target[2]"_log";
    }
    {
        print $2" "$3" "$4" "$5" "$6" "$7 > filename
    }
    ' sorted

# Finally, upload logfiles to Swift
COMMON_STORAGE_PREFIX="http://127.0.01:8080/v1/AUTH_"
for file in `ls -1 *_log`; do
    account=`echo $file | cut -d "_" -f 3`
    container=`echo $file | cut -d "_" -f 4`
    storage_url=$COMMON_STORAGE_PREFIX$account
    echo swift upload --os-storage-url=$storage_url $container $file
done

# Cleanup
rm *_log sorted unsorted
