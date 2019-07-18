# Functions for gathering stats about different apps
unread_count() {
    osascript -e 'if application "Microsoft Outlook" is running then tell application "Microsoft Outlook" to unread count of folder "Inbox" of default account'
}

chrome_tabs() {
    osascript -e 'if application "Google Chrome" is running then tell application "Google Chrome" to count every tab of every window'
}

iterm_tabs() {
    osascript -e 'tell application "iTerm" to count every tab of every window' 
}

cpu_temp() {
    ~/Downloads/osx-cpu-temp-1.1.0/osx-cpu-temp -C | cut -f1 -d°
}
# ps -axrco pcpu,user,command | head -n 10

# Gather various stats and report them to Kinesis stream
while true; do
    CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    UNREAD_COUNT=$(unread_count)
    echo "Unread emails: ${UNREAD_COUNT}"

    CHROME_TABS=$(chrome_tabs)
    echo "Chrome tabs: ${CHROME_TABS}"

    ITERM_TABS=$(iterm_tabs)
    echo "iTerm tabs: ${ITERM_TABS}"

    CPU_TEMP=$(cpu_temp)
    echo "CPU Temp (°C): ${CPU_TEMP}"

    [ -n "${UNREAD_COUNT}" ] && aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"outlook_unread","type":"gauge","value":"'${UNREAD_COUNT}'", "ts":"'${CURRENT_TIME}'"}
' --partition-key 1

    [ -n "${CHROME_TABS}" ] && aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"chrome_tabs","type":"gauge","value":"'${CHROME_TABS}'", "ts":"'${CURRENT_TIME}'"}
' --partition-key 1

    aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"iterm_tabs","type":"gauge","value":"'${ITERM_TABS}'", "ts":"'${CURRENT_TIME}'"}
' --partition-key 1

    aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"cpu_temp","type":"gauge","value":"'${CPU_TEMP}'", "ts":"'${CURRENT_TIME}'", "metadata":{"cpu_temp":{"units":"celsius"}}}
' --partition-key 1
    sleep 10
done
