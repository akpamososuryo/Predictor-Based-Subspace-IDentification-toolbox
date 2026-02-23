classdef TestSmoke < matlab.unittest.TestCase
    % Very small, deterministic test to ensure the toolbox runs.

    methods (Test)
        function dordvarxRuns(testCase)
            rng(0, "twister");

            % Simple stable SISO system (no toolboxes required)
            N = 300;
            u = randn(N,1);
            y = zeros(N,1);
            e = 0.05 * randn(N,1);

            % y(k) = 0.7*y(k-1) + 0.2*u(k-1) + e(k)
            for k = 2:N
                y(k) = 0.7*y(k-1) + 0.2*u(k-1) + e(k);
            end

            % PBSID pre-processing
            f = 5;
            p = 10;

            % Put repo root on the path without genpath (avoids extra/backwards)
            repoRoot = fileparts(fileparts(mfilename("fullpath")));
            addpath(repoRoot);
            cleanup = onCleanup(@() rmpath(repoRoot));

            [S, X] = dordvarx(u, y, f, p);

            % Basic sanity checks
            testCase.verifyNotEmpty(S);
            testCase.verifyNotEmpty(X);
            testCase.verifyTrue(all(isfinite(S)), "S contains NaN/Inf");
            testCase.verifyTrue(all(isfinite(X(:))), "X contains NaN/Inf");

            % Expected dimensions
            testCase.verifyEqual(size(X,2), N - p);
            testCase.verifyEqual(length(S), size(X,1));
        end
    end
end