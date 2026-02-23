function [A, B, C, D] = callDx2abcd(x, u, y, f, p, stableOpt)
%callDx2abcd  Call dx2abcd with signature and option fallbacks.
%
% Tries a few common call patterns for dx2abcd and returns [A,B,C,D].

if nargin < 6
    stableOpt = '';
end

% Candidate calls, ordered from most specific to more generic.
candidates = {};

if ~isempty(stableOpt)
    candidates{end+1} = @() dx2abcd(x, u, y, f, p, stableOpt);
    candidates{end+1} = @() dx2abcd(x, u, y, f, stableOpt);
    candidates{end+1} = @() dx2abcd(x, u, y, stableOpt);
end

candidates{end+1} = @() dx2abcd(x, u, y, f, p);
candidates{end+1} = @() dx2abcd(x, u, y, f);
candidates{end+1} = @() dx2abcd(x, u, y);

lastErr = [];
for i = 1:numel(candidates)
    try
        [A, B, C, D] = candidates{i}();
        return
    catch ME
        lastErr = ME;
    end
end

rethrow(lastErr);
end