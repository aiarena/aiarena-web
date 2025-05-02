#!/usr/bin/env bash
# The handler requires the SENTRY_DSN environment variable to be set.

if [[ $TRACK_REQUEST_FINISHED = 0 ]]
then
  sentry_message="HARAKIRI ON: VIEW: ${TRACK_VIEW}"
  echo_message="${sentry_message} URL: ${TRACK_URI} USER: ${TRACK_USER_ID}"
  echo "$echo_message"
  sentry-cli send-event \
    --env "production" \
    --release "$TRACK_BUILD_NUMBER" \
    --tag server_name:"$TRACK_SERVER_NAME" \
    --message "$sentry_message" \
    --user id:"$TRACK_USER_ID" \
    --extra view:"$TRACK_VIEW" \
    --extra url:"$TRACK_URI" \
    --extra grapqhql_operations:"${TRACK_GRAPHQL_OPERATION_NAMES}" \
    --extra grapqhql_variables:"${TRACK_GRAPHQL_OPERATION_VARS}" \
    --no-environ
fi
