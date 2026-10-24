#!/usr/bin/env bash
# Runs on an existing host. It never provisions resources or invokes a model.
set -Eeuo pipefail
revision=${1:?revision required}
hostname=${2:?hostname required}
[[ $revision =~ ^[a-f0-9]{40}$ ]] || exit 2
[[ $hostname =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$ ]] || exit 2
base=/opt/neuro
state=$base/state
www=/opt/portfolio/www
sites=/opt/portfolio/caddy
archive=$base/neuro-$revision.tgz
release=$base/releases/$revision
test -d "$base/releases" && test -d "$state" && test -d "$www" && test -d "$sites"
test -s "$state/agents.env"
sudo docker network inspect portfolio-edge >/dev/null
sudo docker inspect vigil-web-1 >/dev/null
exec 9>"$base/deploy.lock"
flock -n 9 || { echo 'Another NeuroAgent deployment is active'; exit 1; }
test ! -e "$www/neuro" || test -L "$www/neuro" || { echo 'The frontend path must be absent or a release symlink'; exit 1; }

previous_web=''
if test -L "$www/neuro"; then previous_web=$(readlink "$www/neuro"); fi
previous_compose=false
if test -f "$state/compose.json"; then
  cp -p "$state/compose.json" "$state/compose.before-release.json"
  previous_compose=true
fi
previous_site=false
if test -f "$sites/neuro.caddy"; then
  cp -p "$sites/neuro.caddy" "$state/neuro.before-release.caddy"
  previous_site=true
fi
activated=false
published=false
site_changed=false
rollback() {
  result=$?
  trap - ERR
  set +e
  if $previous_compose; then
    cp -p "$state/compose.before-release.json" "$state/compose.json"
    if $activated; then sudo docker compose -f "$state/compose.json" up -d; fi
  fi
  if $published; then
    if test -n "$previous_web"; then
      ln -s "$previous_web" "$www/.neuro-rollback-$$"
      mv -Tf "$www/.neuro-rollback-$$" "$www/neuro"
    else
      rm -f "$www/neuro"
    fi
  fi
  if $site_changed; then
    if $previous_site; then cp "$state/neuro.before-release.caddy" "$sites/neuro.caddy";
    else rm -f "$sites/neuro.caddy"; fi
    sudo docker exec vigil-web-1 caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
  fi
  echo 'Deployment failed; previous available configuration and frontend were restored. Data volumes were retained.'
  exit "$result"
}
trap rollback ERR

if ! test -d "$release"; then
  staging=$base/releases/.staging-$revision-$$
  mkdir -m 700 "$staging"
  tar -xzf "$archive" -C "$staging"
  test "$(cat "$staging/REVISION")" = "$revision"
  test -s "$staging/frontend-static/index.html"
  test -s "$staging/deploy/oracle/Dockerfile"
  mv "$staging" "$release"
fi
test "$(cat "$release/REVISION")" = "$revision"
python3 "$release/deploy/oracle/prepare.py" --state-dir "$state" --hostname "$hostname" --revision "$revision"
sudo docker compose -f "$state/compose.json" config --quiet
if ! sudo docker image inspect "neuro-api:$revision" >/dev/null 2>&1; then
  sudo docker compose -f "$state/compose.json" build --pull
fi
activated=true
sudo docker compose -f "$state/compose.json" up -d --wait --wait-timeout 300

web_release=$www/.neuro-releases/$revision
if ! test -d "$web_release"; then
  mkdir -p "$web_release"
  cp -a "$release/frontend-static/." "$web_release/"
  chmod -R a+rX "$web_release"
fi
test -s "$web_release/index.html"
ln -s ".neuro-releases/$revision" "$www/.neuro-current-$$"
mv -Tf "$www/.neuro-current-$$" "$www/neuro"
published=true
cp "$state/neuro.caddy" "$sites/neuro.caddy"
chmod 644 "$sites/neuro.caddy"
site_changed=true
sudo docker exec vigil-web-1 caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
sudo docker exec vigil-web-1 caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
python3 "$release/deploy/oracle/verify.py" --hostname "$hostname" --timeout 300
printf '%s\n' "$revision" > "$state/deployed-revision"
trap - ERR
rm -f "$archive"
echo 'Deployment passed routing, authentication and health checks. Live model validation is separate.'
