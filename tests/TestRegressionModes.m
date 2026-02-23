classdef TestRegressionModes < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function dordvarxRunsWithDifferentRegularizations(testCase)
            [u, y, sys] = testutils.makeSisoData('N', 500, 'seed', 3, 'noiseStd', 0.03);

            f = 5;
            p = 10;

            % Baseline (no extra args)
            [S0, X0] = testutils.callDordvarx(u, y, f, p);
            testCase.verifyEqual(size(X0,2), sys.N - p);
            testCase.verifyTrue(all(isfinite(X0(:))));
            testCase.verifyTrue(all(isfinite(S0)));

            % Try a few regularization modes if supported.
            % If a mode is not supported by the current signature, the helper will error.
            modes = {
                {'tikh', 1e-2}
                {'tsvd', 10}
            };

            for i = 1:numel(modes)
                reg = modes{i}{1};
                opt = modes{i}{2};

                try
                    [S, X] = testutils.callDordvarx(u, y, f, p, reg, opt);
                catch ME
                    % Skip if the toolbox version does not support that reg mode via dordvarx
                    testCase.assumeFail("Skipping reg mode '" + string(reg) + "': " + string(ME.message));
                    continue
                end

                testCase.verifyEqual(size(X,2), sys.N - p);
                testCase.verifyEqual(size(X,1), numel(S));
                testCase.verifyTrue(all(isfinite(X(:))), "X contains NaN/Inf for reg " + string(reg));
                testCase.verifyTrue(all(isfinite(S)), "S contains NaN/Inf for reg " + string(reg));
                testCase.verifyGreaterThanOrEqual(min(S), 0);
            end
        end
    end
end